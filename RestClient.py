#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
-------------------------------------------------------------------------------

PROPRIETARY/CONFIDENTIAL
Copyright (c) 2015 Verizon, All Rights Reserved.
Not for disclosure without written permission.

Author:  Vyacheslav Vladyshevsky (vyacheslav.vladyshevsky@intl.verizon.com)
Project: Verizon Cloud Automation

Generic wrapper around Verizon Cloud API.

-------------------------------------------------------------------------------
"""

__author__ = 'Slava Vladyshevsky <vyacheslav.vladyshevsky@intl.verizon.com'
__version__ = '0.1.1'

import base64
import hmac
import hashlib
import httplib
import urllib
import json
import re
import time
import socket
import uuid
import logging as log

# format for the timestamp used in HTTP headers, according to the RFC1123
TIMESTAMP_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
# MIME type definition for the job (status) resource
JOB_MIME_TYPE = 'application/vnd.terremark.ecloud.job.v1+json'
# regex for headers used to generate request signature
HEADER_REGEX = '^x-tmrk-(?!authorization)'
# HTTP user agent
USER_AGENT = 'VACli/%s' % __version__
# maximum number of HTTP redirects to follow
MAX_REDIRECTS = 3
# supported API version
API_VERSION = '2015-05-01'
# implemented API verbs
API_VERBS = [
    'GET',      # retrieve a single or collection of resources
    'POST',     # create a new resource in a collection
    'PUT',      # replace a resource
    'PATCH',    # update a resource
    'DELETE',   # delete a resource
    'OPTIONS'   # discover available methods and other options for a resource
]


class ArgumentException(Exception):
    pass


class APIException(Exception):
    pass


class CloudApiAuth(object):
    """ CloudApi authentication method implementation. Currently the only auth method supported by George.

    CloudApi authorization uses a shared secret to calculate an HMAC (Hash-based Message Authentication Code) signature
    over the request body to provide request authenticity and prevent tampering. The HMAC digest assures:

    - Integrity and authentication
    - The request has not been altered in transit
    - Only those who know the secret key could produce the digest

    See http://cloud.verizon.com/documentation/APIAuthentication_1.htm
    """
    __name__ = 'CloudApiAuth'

    def __init__(self, key_id, secret_key):
        self.header_prefix = re.compile(HEADER_REGEX, re.I)
        self.key_id = str(key_id)
        if not self.key_id:
            raise ArgumentException("No key ID provided")

        self.secret_key = str(secret_key)
        if not self.secret_key:
            raise ArgumentException("No secret key provided")

    def add_auth_headers(self, verb, headers, path, query):
        """ Adds HMAC signed authorization header

        Authorization: CloudApi AccessKey="{accessKey}" SignatureType="{signatureType}" Signature="{signature}"
        """
        headers['Date'] = time.strftime(TIMESTAMP_FORMAT, time.gmtime())
        base64_hmac = base64.encodestring(
            hmac.new(self.secret_key,
                     self._signature(verb, headers, path, query),
                     digestmod=hashlib.sha256
                     ).digest()
        ).strip()

        headers['x-tmrk-authorization'] = \
            'CloudApi AccessKey="%s" SignatureType="%s" Signature="%s"' % (self.key_id, 'HmacSHA256', base64_hmac)

    def _canonical_headers(self, headers):
        """ Build a canonical headers string.

        The canonical headers are a list of all request headers that begin with x-tmrk-,
        excluding the x-tmrk-authorization header. Canonical headers are constructed using
        the following steps:

        1. Retrieve all headers for the resource that begin with x-tmrk- prefix (excluding x-tmrk-authorization).
        2. Convert each HTTP header field name to lowercase.
        3. Sort the header fields lexicographically in ascending order by header field name.
           Note: Each header may appear only once in the string.
        4. Unfold the string by replacing any breaking whitespace with a single space.
        5. Trim any whitespace around the colon in the header field.
        6. Append a newline character to each header field in the resulting list.
        7. Concatenate all headers in this list into a single string.

        See http://cloud.verizon.com/documentation/APIAuthentication_1.htm
        """
        matching_headers = {k.lower(): v for k, v in headers.items() if self.header_prefix.match(k)}
        return '\n'.join(
            ['%s:%s' % (k, v) for k, v in sorted(matching_headers.items())]
        )

    def _canonical_resources(self, path, query):
        """ Build a canonical resources string.

        The canonical resource represents the HTTP resource (path and query-string) of the request. The canonical
        resource is constructed using the following steps:

        1. Use the decoded URL for the resource, converted to lowercase, as the source for the CanonicalizedResource.
        2. Append the resource's URI path, which is the portion of the call after the host and before any query
           component parameters, followed by a newline ("/n") character. The query component of a URI is the part of
           the URI after the "?" character, e.g. /api/resource?{parameter=value}
        3. Retrieve all query component parameters on the resource URL. Query component parameters are separated by the
           ampersand ("&") character, e.g. /api/admin/apikey/[?[offset=x][&limit=y]]
        4. Convert all parameter names to lowercase.
        5. Sort the query parameters lexicographically by parameter name, in ascending order.
        6. Append each query component parameter name and value to the string, in order, in the following format,
           making sure to include the colon (:) between the name and the value, followed by a newline character after
           each name-value pair, e.g. {parameter}:{value}\n

        See http://cloud.verizon.com/documentation/APIAuthentication_1.htm
        """
        # TODO: decode URL for the resource
        if not query:
            return path.lower()

        arg_list = [path.lower()]
        for kv in query.split('&', 1):
            k, v = kv.split('=', 1)
            arg_list.append('%s:%s' % (k.lower(), v))

        return '\n'.join(sorted(arg_list))

    def _signature(self, verb, headers, path, query):
        """ Build a signature string

        stringToSign = {VERB} "\n"
                       {Content-Length} "\n"      <-- this one in eCLoud specification only, though VecA taking it too
                       {Content-Type} "\n"
                       {Date} "\n"
                       {CanonicalizedHeaders}
                       {CanonicalizedResource}

        See http://cloud.verizon.com/documentation/APIAuthentication_1.htm
        """
        signature = "\n".join(
            [
                verb,
                headers.get('Content-Length', ''),
                headers.get('Content-Type', ''),
                headers['Date'],
                self._canonical_headers(headers),
                self._canonical_resources(path, query),
                ''  # adding empty element for a trailing new-line
            ])
        log.debug('%s.signature: %s' % (self.__name__, signature))
        return signature


class RestClient(object):
    __name__ = "RestClient"

    @staticmethod
    def print_json(data):
        print json.dumps(data, indent=2, separators=(',', ': '), sort_keys=True)

    @staticmethod
    def print_table(data, keys, empty='#', header=True):
        if data and keys:
            rows = [[str(item.get(k, empty)) for k in keys] for item in data]  # extracting given keys from collection
            if header:
                rows.insert(0, keys)    # inserting those keys as a header line
            cols = zip(*rows)           # reorganizing data by columns
            col_widths = [max(len(val) for val in col) for col in cols]     # compute column widths as max value length
            fmt = ' '.join(['%%-%ds' % width for width in col_widths])      # create a suitable format string
            for row in rows:
                print fmt % tuple(row)  # print each row using the computed format

    def __init__(self, base_url, auth, account=None, cloudspace=None):
        log.info('%s.init(base_url: %s)' % (self.__name__, base_url))
        url_parts = httplib.urlsplit(base_url)
        self.host = url_parts.hostname
        self.scheme = url_parts.scheme
        self.auth = auth
        self.account = account
        self.cloudspace = cloudspace
        self.conn = None
        self.cache = {}
        self.redirect_attempt = 0

    def get_root_master(self):
        log.info("%s.get_root_master()" % self.__name__)
        href = "%s://%s/api/" % (self.scheme, self.host)
        return self.get(href)

    def get_root(self, tag=None):
        log.info("%s.get_root(tag: %s)" % (self.__name__, tag))
        href = "%s://%s/api/compute" % (self.scheme, self.host)
        if tag:
            href = "%s/tag/%s" % (href, tag)

        if href in self.cache:
            root = self.cache[href]
            log.info("%s.get_root(...): cache hit for href: %s" % (self.__name__, href))
        else:
            root = self.get(href)
            self.cache[href] = root
        return root

    def get_href(self, group=None, tag=None, ref=None):
        log.info('%s.get_href(group: %s, tag: %s, ref: %s)' % (self.__name__, group, tag, ref))
        root = self.get_root(tag)
        href = root[group]['href'] if group in root else None
        # creating HREF out of resource reference ref
        if ref:
            if ref.lower().startswith('http'):
                href = ref
            elif href:
                href = '%s%s' % (href, ref)

        return href

    def request(self, verb, url, headers, body):
        verb = verb.upper()
        log.info('%s.request(verb: %s, url: %s)' % (self.__name__, verb, url))

        if verb not in API_VERBS:
            raise ArgumentException('HTTP method "%s" is not implemented' % verb)
        if not url:
            raise ArgumentException('Missing URL for HTTP request')

        # making sure the last connection has been terminated properly
        if self.conn:
            self.conn.close()

        # decoding URL, just a safety net, shouldn't be needed normally
        url = urllib.unquote(url.encode('ascii')).decode('utf-8')
        url_parts = httplib.urlsplit(url)
        resource = url_parts.path + '?' + url_parts.query if url_parts.query else url_parts.path
        if url_parts.hostname:
            self.host = url_parts.hostname
        if url_parts.scheme:
            self.scheme = url_parts.scheme

        # we'll support plain HTTP, though HTTPS is a clear preference, obviously
        if self.scheme == 'http':
            self.conn = httplib.HTTPConnection(self.host)
        elif self.scheme == 'https':
            self.conn = httplib.HTTPSConnection(self.host)
        else:
            raise APIException('Unsupported protocol: %s' % self.scheme)

        # TODO: the data has to be encoded
        # body = urllib.urlencode(data)
        request_headers = {
            # these two headers required if multiple cloud-spaces belong to the same account
            'x-tmrk-acct': self.account,
            'x-tmrk-cloudspace': self.cloudspace,
            'x-tmrk-dc': '%s://%s' % (self.scheme, self.host),
            # x-tmrk-nonce header holds an optional random, unique identifier for each request. API services do not
            # allow a request with the same nonce to be replayed, guarding against replay attacks. The nonce should
            # be as unique as required, otherwise, if multiple clients using the same keys are executing requests
            # simultaneously there is a chance of collision.
            'x-tmrk-nonce': uuid.uuid1(),
            # header required by eCloud API, it's not used and tolerated by George
            'x-tmrk-version': API_VERSION,
            # custom headers
            'Accept-Language': 'en-US',
            'User-Agent': USER_AGENT
        }

        # giving a chance to comprehend and/or override request headers
        if headers:
            request_headers.update(headers)

        self.auth.add_auth_headers(verb, request_headers, url_parts.path, url_parts.query)

        log.debug('%s.request:headers: \n%s' %
                  (self.__name__, '\n'.join(['%s: %s' % (k, v) for k, v in request_headers.items()])))
        log.debug('%s.request:body: \n%s' % (self.__name__, body))

        try:
            self.conn.request(verb, resource, body, request_headers)
            response = self.conn.getresponse()
            response_body = response.read()
            response.close()

        except socket.error, (rc, msg):
            raise APIException("Got socket error (%d) %s" % (rc, msg))
        except httplib.ResponseNotReady:
            raise APIException("Got ResponseNotReady exception")

        log.info('%s.response: %d %s' % (self.__name__, response.status, response.reason))
        log.debug('%s.response:headers: \n%s' %
                  (self.__name__, '\n'.join(['%s: %s' % (k, v) for k, v in response.getheaders()])))

        # HTTP 3xx - redirect
        if response.status in [httplib.MOVED_PERMANENTLY, httplib.FOUND, httplib.SEE_OTHER]:
            self.redirect_attempt += 1
            # we will handle only as many redirects to avoid endless loops
            if self.redirect_attempt < MAX_REDIRECTS:
                return self.request(verb, response.getheader('Location'), request_headers, body)
            else:
                raise APIException('Gave up after %d redirects' % MAX_REDIRECTS)

        # clearing counter upon non-redirect response
        self.redirect_attempt = 0

        # HTTP 2xx - success
        if response.status in [httplib.OK, httplib.CREATED, httplib.ACCEPTED, httplib.NO_CONTENT]:
            try:
                resp_json = json.loads(response_body) if response_body else {}
            except Exception, ex:
                log.debug('%s.response body: %s' % (self.__name__, response_body))
                raise APIException('JSON response parse error: %s' % ex)

            return resp_json

        # HTTP 4xx and 5xx - errors
        """
        The George REST API is generating JSON response with error message and status code, e.g.

        {
          "description": "Error",
          "message": "Conflict : vnet must have no vm's attached",
          "statusCode": 409,
          "type": "application/vnd.terremark.ecloud.full-response.v1+json"
        }

        The eCloud REST API is generating XML response with error message and status code, e.g.

        <Error message="Authentication is required." majorErrorCode="401" minorErrorCode="AuthenticationRequired"/>
        """
        raise APIException("%d %s\n%s" % (response.status, response.reason, response_body))

    def get_array(self, url, extra_headers={}):
        items = []
        next_href = url
        while next_href:
            page = self.get(next_href, extra_headers)
            next_href = page['next']['href'] if 'next' in page else None
            items += page['items']
        return items

    def get(self, url, extra_headers={}):
        return self.request('GET', url, extra_headers, None)

    def options(self, url, extra_headers={}):
        return self.request('OPTIONS', url, extra_headers, None)

    def delete(self, url, extra_headers={}):
        headers = {
            'Accept': JOB_MIME_TYPE
        }
        if extra_headers:
            headers.update(extra_headers)

        return self.request('DELETE', url, headers, None)

    def post(self, url, data=None, extra_headers={}):
        headers = {
            'Accept': JOB_MIME_TYPE,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        if data:
            if data.get('type'):
                headers["Content-Type"] = data['type']
            data = json.dumps(data)

        if extra_headers:
            headers.update(extra_headers)

        return self.request('POST', url, headers, data)

    def patch(self, url, data, extra_headers={}):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        if data:
            data_type = data.get('type')
            if data_type:
                headers['Accept'] = data_type
                headers["Content-Type"] = data_type
            data = json.dumps(data)

        if extra_headers:
            headers.update(extra_headers)

        return self.request('PATCH', url, headers, data)

    def put(self, url, data, extra_headers={}):
        headers = {
            'Content-Type': 'application/vnd.terremark.ecloud.job.v1+json',
            'Accept': '*/*'
        }

        if data:
            data_type = data.get('type')
            if data_type:
                # headers['Accept'] = data_type
                headers["Content-Type"] = data_type
            data = json.dumps(data)

        if extra_headers:
            headers.update(extra_headers)

        return self.request('PUT', url, headers, data)

    def poll_jobs(self, jobs, poll_interval=5, timeout=300):
        log.info('%s.wait_jobs(%d/%d) starting poll for %s' % (self.__name__, poll_interval, timeout, jobs))
        running_jobs = jobs if isinstance(jobs, list) else [jobs]
        result = {}
        start_time = time.time()
        while running_jobs and time.time() - start_time < timeout:
            for job_href in running_jobs:
                job = self.get(job_href)
                result[job_href] = job
                status = job['status']
                log.info(
                    "job id: %s name: %s status: %s progress: %d%%" % (job['id'], job['name'], status, job['progress']))
                if status in ['COMPLETE', 'CANCELED', 'CANCELING', 'FAILED']:
                    running_jobs.remove(job_href)
            # first poll then wait if job list is not empty
            if len(running_jobs):
                time.sleep(poll_interval)

        return result
