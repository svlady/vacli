### SUMMARY

The VACLI project has been inspired by AWSCLI utility and provides similar
REST API access functionality for the Verizon VCC platform, also historically 
known as Project George or Vector A.

Below is the list of the most important features:

* provides a standalone reference VCC REST API client implementation
* self-sufficient, no external libraries or dependencies
* highly configurable (via JSON config file, ENV variables, CLI switches)
* supports multiple configuration profiles
* supports command line auto-completion in BASH shell
* provides advanced logging capabilities
* supports primitive HTTP commands for low-level requests
* provides significant VCC REST API coverage
* supports both short (UUID) and long (HREF) resource IDs for addressing
* supports both JSON and tabular output formatting
* extended support for resource tags
* supports HTTP/HTTPS proxies

The package includes everything to get you started:

    Readme.md       - the file you're reading
    .vacli_example  - the example configuration file (in JSON format)
    RestClient.py   - the Python module implementing a generic REST API wrapper
    vacli           - the CLI tool providing human interface for the API
    vacli.bash      - the BASH script to be sourced for shell auto-completion
    vacli.env       - the BASH script to be sourced for ENV variables setup
    vacli.tmp       - the API cache file, stores immutable API call results

Make sure to check the FAQ section at the end of the document. Chances are -
some of your questions are already answered there.


### SUPPORT
This project provided as example code only, meaning that there is no support
commitment or obligations. Saying that, the package author and the team of
maintainers may provide some support on a best-effort basis as time permits.

If you have any questions, suggestions or comments - feel free to contact:

    Slava Vladyshevsky <slava.vladyshevsky(a)gmail.com>
    Andy Stenger <andy.stenger(a)gmail.com>


### PREREQUISITES
Due to the syntax and compatibility constraints the tool is supported for
the Python version 2.7.x only. Unfortunately, earlier 2.x and later versions 
3.x are not supported due to the syntax changes and compatibility constraints. 
Both Windows, Linux and MacOS versions were tested.


### SETUP
There is no real setup required. The tool does not depend on any external 
modules or libraries and may be used right away as soon as you have your 
credentials and API access point details setup. The configuration options 
may be specified in several ways:

#### Configuration File .vacli
You can put your access and secret key as well as some additional parameters
into the ```.vacli``` configuration file, which is normally placed in the folder,
where the VACLI tool itself resides. Shall you need to use configuration 
located elsewhere make sure you added the ```--config-file``` switch to tell, 
where to look for the settings

In the example below, the "default" subsection in JSON is a so called profile.
You may define multiple profiles and switch between them using the 
```--profile``` option. If no profile specified, the "default" profile is used.

```
$ cat .vacli_example
{
   "default": {
     // optional proxy, can be removed for direct access to the API endpoint
     "http_proxy": "proxy.....com:80",

     // the following are essential parameters defining your credentials
     "api_account": "720438c0-...",
     "api_cloud_space": "60f28e75-...",
     "api_access_key": "6451af2...",
     "api_secret_key": "RrIOESzok...",
     "api_endpoint": "https://amsa1.cloud.verizon.com"
   }
}

# Using alternative config file location
$ ./vacli --config-file /etc/vacli/vacli.cfg --profile default get-root

```

#### Shell Environment Variables
You can specify (or override) all or some configuration parameters using the 
shell environment variables. For example:

```
$ cat vacli.env

API_USER="john.doe@mail.com"
API_ORG="f43a0037-..."
API_ACCOUNT="720438c0-..."
API_CLOUD_SPACE="60f28e75-..."
API_ACCESS_KEY="6451af2..."
API_SECRET_KEY="RrIOESzok..."
API_ENDPOINT="https://amsa1.cloud.verizon.com"
HTTP_PROXY="http://myproxy.corporate.com"

export API_USER API_ORG API_ACCOUNT API_CLOUD_SPACE \
API_ACCESS_KEY API_SECRET_KEY API_ENDPOINT HTTP_PROXY
```

#### Command Line Switches
Eventually, you can specify (or override) all or some configuration parameters
using command line arguments. For example:

```
$ ./vacli --api-access-key="6451af2..." --api-secret-key="RrIOESzok..." get-root-master
```

Obviously, you can combine all three methods too. In this case the config 
file values are overridden by the environment variable, which are, in turn, 
overridden by the command line options.

### USING PROXY
Sometimes egress HTTP/HTTPS calls are not allowed and the only way to access
the API endpoint is using HTTP proxy. Like the other settings a proxy can be 
specified using either configuration file, environment variable or the 
corresponding command-line option, e.g.

```
$ HTTP_PROXY=XX.XX.XX.XX:3128 ./vacli --log-level info get-root
$ ./vacli --http-proxy XX.XX.XX.XX:3128 --log-level info get-root

2015-08-25 15:15:36 INFO: RestClient.init(base_url: https://amsa1.cloud.verizon.com)
2015-08-25 15:15:36 INFO: RestClient.get_root(tag: None)
2015-08-25 15:15:36 INFO: RestClient.request(verb: GET, url: https://amsa1.cloud.verizon.com/api/compute)
2015-08-25 15:15:36 INFO: RestClient.request via proxy XX.XX.XX.XX:3128
2015-08-25 15:15:39 INFO: RestClient.response: 200 OK
{
   "description": "This is a resource root entry point for the REST API",
   "href": "https://amsa1.cloud.verizon.com/api/compute",
...
```
Note: the SOCKS protocol and proxy auth are not supported.

### API PERFORMANCE AND CACHING
One of the REST API benefits - using HTTP protocol as its transport - at the
same time often becoming one of its major shortcomings. Try to add SSL to the 
mix and the proxy server in between and previously quick and responsive API 
calls all the sudden becoming sluggish and slow. Now, run a loop to process 
hundreds API calls and ... go get your favorite beverage.

Obviously, besides finding a quick (low latency) and responsive proxy server 
not much can be done to resolve the aforementioned issue. However, some little 
improvements may be still achieved by caching some API call responses and thus 
reducing overall communication duration times.

#### Caching API calls
Generally speaking, the caching itself may be both good and evil, especially 
in case of stateless REST-based communication, therefore special care must be 
taken and attention paid to what is cached exactly and for how long.

At the same time, caching fairly immutable API responses must be safe enough 
and may help improving API performance without sacrificing accuracy or its
reliability.

The VACLI does implement this idea and caches only immutable data in the local 
file-system file ```vacli.tmp```. Normally, you don't need to care much about 
this cache, clean or flush it, when moving to a different endpoint or 
environment. It will be flushed or updated automatically.

```
$ ./vacli --log-level info list-vms --table
2015-10-05 12:13:14 INFO: RestClient.init(base_url: https://amsa1.cloud.verizon.com)
2015-10-05 12:13:14 INFO: RestClient.init(): reading API cache file vacli.tmp
```
... the line above tells that cache file has been found and read successfully
```
2015-10-05 12:13:14 INFO: RestClient.get_href(group: vms, tag: None, ref: None)
2015-10-05 12:13:14 INFO: RestClient.get_root(tag: None)
2015-10-05 12:13:14 INFO: RestClient.get_root(): cache hit for href: https://amsa1.cloud.verizon.com/api/compute
```
... and here we can see that we already saved one API call by hitting the cache
```
2015-10-05 12:13:14 INFO: RestClient.request(verb: GET, url: https://amsa1.cloud.verizon.com/api/compute/vm/?limit=100)
2015-10-05 12:13:16 INFO: RestClient.request: TTFB: 2.151 sec, response read: 0.085 sec
```
... now the time to the first byte (TTFB) and time used for fetching response is measured as well
```
2015-10-05 12:13:16 INFO: RestClient.response: 200 OK
```

#### Decreasing API chattiness
As you may have seen from above example, there is a significant difference
between TTFB and response read times, pointing back to the same issue -
protocol latency. Without diving deep and discussing more advanced
optimization options, the long story short - the less the number of HTTP
request/response cycles, the less overall API transaction time is going to be.

Employing caches may help to save on some API calls and another improvement
is coming from the API feature allowing to fetch so called "deep" JSON, where 
referenced objects are fully populated not a mere HREF links.

It may be explained the best by example. Say, we need to find all IP addresses
belonging to the given VMs, as well as information about all disks volumes 
attached to it. The usual approach is going to be:
- to fetch VM objects (1-N x API calls)
- for each VM fetch "vnics" collection (N x API calls)
- for each VM fetch "vdiskMounts" collection (N x API call)

It's easy to see that as number of VM grows, the number of required API
calls grows linearly along with it. Thus for N VMs, we're talking about 3 x N 
API calls at least.

The good news - starting from GOL 1.9.10, it's possible to pack it all into
a single API call, e.g.
```
$ ./vacli get --href https://iadb1.cloud.verizon.com/api/compute/vm/?expand=_item.vdiskMounts,_item.vnics
```

This API call will fetch "vnics" and "vdiskMounts" data along with other VM 
details in one shot. Considering the TTFB time as the major contributing factor
to communication delays, by emplying this technique, the whole transaction 
duration can be significantly cut down.

### LOGGING AND DEBUGGING

#### Increasing output verbosity
Sometimes you may want to increase output (or logging) verbosity to see the 
specific API calls performed, their inputs and output. For this, use the 
```--log-level`` global option. The "info" log-level does already provide a 
lot of details. The "debug" log-level goes even further, providing raw 
HTTP request/response details.

#### Storing log messages to the file
If you don't want to clutter output with additional debug messaged, you can 
divert them to the file by using the ```--log-file``` global option. By default
the STDOUT is used for the log messages.
```
$ ./vacli --log-level info --log-file vacli.log get-root
{
   "description": "This is a resource root entry point for the REST API",
   "href": "https://amsa1.cloud.verizon.com/api/compute",
   "ipAddresses": {
     "description": "A collection of IP address entities that are in the public IP space and accessible to the authenticated user.",
     "href": "https://amsa1.cloud.verizon.com/api/compute/ip-address/",
     "type": "application/vnd.terremark.ecloud.ip-address.v1+json; type=group"
   },
...

$ cat vacli.log
2015-11-20 14:53:26 INFO: RestClient.init(base_url: https://amsa1.cloud.verizon.com)
2015-11-20 14:53:26 INFO: RestClient.init(): reading API cache file vacli.tmp
2015-11-20 14:53:26 INFO: RestClient.get_root(tag: None)
2015-11-20 14:53:26 INFO: RestClient.get_root(): cache hit for href: https://amsa1.cloud.verizon.com/api/compute
2015-11-20 14:54:10 INFO: RestClient.init(base_url: https://amsa1.cloud.verizon.com)
2015-11-20 14:54:10 INFO: RestClient.init(): cannot read cache
2015-11-20 14:54:10 INFO: RestClient.get_root(tag: None)
2015-11-20 14:54:10 INFO: RestClient.request(verb: GET, url: https://amsa1.cloud.verizon.com/api/compute)
2015-11-20 14:54:12 INFO: RestClient.request: TTFB: 1.097 sec, response read: 0.000 sec
2015-11-20 14:54:12 INFO: RestClient.response: 200 OK
2015-11-20 14:54:12 INFO: RestClient.get_root(): flushing cache
```

### AUTOCOMPLETION

#### Bash auto-completiong setup

If you want to enable Bash auto-completion, you have to source vacli.bash file, 
e.g.
```
$ . vacli.bash
```
Wasn't it easy?

#### Using Bash auto-completion
Just type ./vacli and press the TAB key twice. This will produce a list with 
available commands, e.g.
```
$ ./vacli <double TAB here>
delete                get-admin-root        list-vdisk-templates  list-vnics            public-ip-del         
vdisk-edit            vm-edit               fw-acl-add            get-resource-groups   list-vdisks
options               public-ip-list        vm-add-vdisk          vm-list-mounts        fw-acl-del
get-root              list-vm-templates     patch                 put                   vm-add-vnic
vnet-create           fw-acl-list           job-list              list-vms              post
update-iops           vm-create             vnet-edit             get                   job-poll
list-vnets            public-ip-add         vdisk-create          vm-ctl                vnic-edit
$ ./vacli
```

After typing a command you can either supply the ```-h``` option and see the 
additional help message for this particular command or enter ```--``` 
(double-dash) and use double TAB to see options accepted by this command, e.g.
```
$ ./vacli job-list -h
usage: vacli job-list [-h] [--last [N]] [--table [key [key ...]]]

optional arguments:
   -h, --help            show this help message and exit
   --last [N]            show last N jobs, default: 10
   --table [key [key ...]]
                         format output as a human readable table with given
                         keys

$ ./vacli job-list --<double TAB here>
--last   --table
$ ./vacli job-list --last 5 --table
startTime      operation          target.href                                                                                  status
09/03/15 11:32 POWER_OFF_VM       https://amsa1.cloud.verizon.com/api/compute/vm/ed23357d-2778-412e-995f-2cc0ef984160          COMPLETE
11/10/15 12:05 ALLOCATE_IPADDRESS https://amsa1.cloud.verizon.com/api/compute/ip-address/3fb19d38-6088-4492-b1b4-91d230a15566  COMPLETE
11/17/15 14:30 CREATE_VDISK       https://amsa1.cloud.verizon.com/api/compute/vdisk/c8992962-32af-4e78-bfa2-ad08f7509e7d       COMPLETE
11/17/15 14:32 CREATE_VDISK_MOUNT https://amsa1.cloud.verizon.com/api/compute/vdisk-mount/b13ff15a-5674-4da9-87de-e29c97f03471 COMPLETE
11/17/15 14:34 DELETE_VM          https://amsa1.cloud.verizon.com/api/compute/vm/bc2ce4e9-3768-467c-8ac6-eb4215e1c8e8          COMPLETE
```

#### Some clever tricks
It's not all, there is some magic too! Let's imagine you want to list all 
firewall ACLs, but you don't recall the IP assigned, let alone their assigned 
resource UUIDs... Auto-completion is your friend, e.g.

```
$ ./vacli fw-acl-list --ip <double TAB here>
xxx.151.224.199  xxx.151.224.2    xxx.151.224.200  xxx.151.224.22   xxx.151.224.99   xxx.151.225.0    xxx.151.225.100
$ ./vacli fw-acl-list --ip xxx.151.22
```

Furthermore, all command-line switches accepting values from a predefined set, can
generate hints and auto-complete your input, e.g.

```
$ ./vacli --log-level <double TAB>
critical  debug     error     info      warning

$ ./vacli fw-acl-add --<double TAB>
--action    --dst-cidr  --idx       --ip-ref    --src-cidr
--dry-run   --dst-port  --ip        --proto     --src-port

$ ./vacli fw-acl-add --action <double TAB>
ACCEPT   DISCARD  REJECT

$ ./vacli fw-acl-add --action DISCARD --proto <double TAB>
ALL   ESP   ICMP  TCP   UDP
```
and so on...

### USAGE EXAMPLES

#### Formatting Output
All vacli commands normally producing a JSON output. You can use *jmespath* or
*jq* tools to query and filter resulting JSON and chain multiple calls using 
the UNIX pipes.

Sometimes, however, it's more convenient to work with a tabular, human readable 
output. Most commands accepting the ```--table``` option and printing certain 
JSON keys as table columns.

```
$ ./vacli public-ip-list
[
   {
     "address": "xxx.151.224.22",
     "creator": {
       "href": "https://amsa1.cloud.verizon.com/api/admin/user/d0f7f6c2-256b-4330-9a42-d3bfb82e94a0",
       "id": "d0f7f6c2-256b-4330-9a42-d3bfb82e94a0",
       "loginId": "apiuser/894140b8-6084-4337-b294-e93f5429b868",
...
$ ./vacli public-ip-list --table
12909981-7712-44aa-97a2-456bc92c1fb0 xxx.151.224.22  Public IP V4
31502523-8fb3-4e53-968e-11f36e7776e0 xxx.151.224.2   Public IP V4
...
```

The ```--table``` option may also be instructed to produce the table with 
specific keys only, instead of the default set, e.g.

```
$ ./vacli public-ip-list --table address v href
xxx.151.224.22  V4 https://amsa1.cloud.verizon.com/api/compute/ip-address/12909981-7712-44aa-97a2-456bc92c1fb0
xxx.151.224.2   V4 https://amsa1.cloud.verizon.com/api/compute/ip-address/31502523-8fb3-4e53-968e-11f36e7776e0
```

You can prepend the list of keys with the "+" modifier to print those keys as
the column headers in the resulting table:

```
$ ./vacli public-ip-list --table + id address name v
id                                   address         name      v
12909981-7712-44aa-97a2-456bc92c1fb0 xxx.151.224.22  Public IP V4
31502523-8fb3-4e53-968e-11f36e7776e0 xxx.151.224.2   Public IP V4
...
```
 
Eventually, you can even use even reference *compound* keys by chaining the 
JSON keys for nested collections. For example:

```
$ ./vacli public-ip-list --table + id v address creator.loginId
id                                   v  address         creator.loginId
ae50ca4e-4c5e-4e34-941d-0ae39f0a56e7 V4 xxx.151.225.100 apiuser/894140b8-6084-4337-b294-e93f5429b868
0b982510-c04c-42ef-90b2-a0cf7b6b2234 V4 xxx.151.225.0   apiuser/894140b8-6084-4337-b294-e93f5429b868
```

The ```--table``` option is supported for both cases, when fetched JSON object 
has a known scheme (default table columns may already be defined) as well as 
for the low-level HTTP verbs, when scheme is, generally speaking, not known 
prior to making a call. Still you can define keys that will be used to format
output table, e.g.

```
$ ./vacli get --href https://amsa1.cloud.verizon.com/api/compute/vm/ --table + id name os status
id                                   name        os                     status
346dd11b-307b-4798-8a9f-b5512a53fb22 PerfKit2    UBUNTU_64              OFF
54619f12-fcec-42ce-a48f-e2ed990f3441 Test Web 02 WINDOWS_SERVER_2008_64 ON
...

$ ./vacli list-vms --table +
id                                   status os                     name        description
346dd11b-307b-4798-8a9f-b5512a53fb22 OFF    UBUNTU_64              PerfKit2    PerfKit Benchmarker 02
54619f12-fcec-42ce-a48f-e2ed990f3441 ON     WINDOWS_SERVER_2008_64 Test Web 02 Web Server 02
...
```

#### Using Tags
The tags attached to various resource instances is a handy mechanism for grouping
resources and may be used by many commands to filter resources by specified tag, e.g.
```
$ ./vacli list-vms --tag api --table +
id                                   status   os        name   description
30946c9a-a16a-489e-86ee-dc45f42a47d2 STARTING UBUNTU_64 DELME3 API Test
ad4b9ce1-0981-4cc6-890d-b3552fd7bd4c ON       UBUNTU_64 DELME2 API Test

$ ./vacli list-vms --tag win2012 --table +
id                                   status os                     name        description
7047c7e9-b52f-4e4c-a2e4-2417036281e1 ON     WINDOWS_SERVER_2008_64 Test SQL 02 Test SQL 2012 AlwaysOn Server
7311df19-4fdf-45d3-83dd-050014c35311 ON     WINDOWS_SERVER_2012    winsvr02    Windows 2012 Server with SQL2012
889f7168-b47a-4b8c-bfc2-3cc36ef90653 ON     WINDOWS_SERVER_2008_64 Test SQL 03 Test SQL 2012 AlwaysOn Server
a6998a94-6c02-4f7b-95c9-6640dc31c3fc ON     WINDOWS_SERVER_2012    Test RDP GW RDP Gateway for TEST Domain
```

Use ```get-tags``` command to fetch a list of all defined tags, e.g.

```
$ ./vacli get-tags --table +
name                                    href
env:test                                https://amsa1.cloud.verizon.com/api/compute/tag/env:test
demo                                    https://amsa1.cloud.verizon.com/api/compute/tag/demo
msadc                                   https://amsa1.cloud.verizon.com/api/compute/tag/msadc
gateway                                 https://amsa1.cloud.verizon.com/api/compute/tag/gateway
jumphost                                https://amsa1.cloud.verizon.com/api/compute/tag/jumphost
firewall                                https://amsa1.cloud.verizon.com/api/compute/tag/firewall
```

You can remove all tags assigned to a resource by providing an empty value to 
the ```--tags``` parameter:

```
$ ./vacli vm-edit --vm bc2ce4e9-3768-467c-8ac6-eb4215e1c8e8 --tags ''

```

You can replace existing tags by providing a new list of tags:

```
$ ./vacli vm-edit --vm bc2ce4e9-3768-467c-8ac6-eb4215e1c8e8 --tags api role:none app:test env:test
...
  "tags": [
    "env:test",
    "api",
    "app:test",
    "role:none"
  ],
...

```

You can append new tags to the existing tags collection. For this you'll need 
to use the "+" modifier.

```
$ ./vacli vm-edit --vm bc2ce4e9-3768-467c-8ac6-eb4215e1c8e8 --tags + group:trial env:test

...
  "tags": [
    "env:test",
    "api",
    "app:test",
    "role:none",
    "group:trial"
  ],
...

```

Note: duplicates will be removed automatically and corresponding tags will be used only once.

#### Referencing Objects
Every object in Verizon Cloud can be referenced by its URL (or HREF) and all 
VACLI commands accepting HREFs. For example:
```
$ ./vacli list-vms --tag pfsense --table + id name href
id                                   name     href
d5372f49-4df4-4d8a-8cbf-f39a3c85a48b fw-auto  https://amsa1.cloud.verizon.com/api/compute/vm/d5372f49-4df4-4d8a-8cbf-f39a3c85a48b
ac633b5d-7675-4f49-b558-ee34d9ae3825 test-fw  https://amsa1.cloud.verizon.com/api/compute/vm/ac633b5d-7675-4f49-b558-ee34d9ae3825
3d7406f5-9206-4419-84cc-cd2f4ea924c2 front-fw https://amsa1.cloud.verizon.com/api/compute/vm/3d7406f5-9206-4419-84cc-cd2f4ea924c2
```
As you can see, the HREF includes both:
- API endpoint: https://amsa1.cloud.verizon.com
- API root: /api/compute
- resource type: /vm
- resource UUID: d5372f49-4df4-4d8a-8cbf-f39a3c85a48b

```
$ ./vacli get --href https://amsa1.cloud.verizon.com/api/compute/vm/d5372f49-4df4-4d8a-8cbf-f39a3c85a48b
[
   {
     "arch": "x86_64",
     "consoleHref": ...
```

In most cases, however, when resource type is defined by the context, it's 
sufficient to provide UUID only and complete HREF may be easily constructed 
on the fly.

In the example above we had to use HREF, since it's not clear from the context
what kind of resource we are requesting. In the next example, using complete 
HREF is superfluous, since it's clear that we're referencing the IP address 
resource:

```
$ ./vacli fw-acl-list --ip-ref https://amsa1.cloud.verizon.com/api/compute/ip-address/5d6df920-39e1-447a-9dd6-e8bb2c621a01 --table +
idx action  protocol sourceIpv4Cidr sourcePorts destinationIpv4Cidr destinationPorts
 0   ACCEPT  TCP      0.0.0.0/0      0           xxx.151.224.200/32  443
 1   DISCARD ALL      0.0.0.0/0      0           xxx.151.224.200/32  0
```

So, the same may be achived by using the resource UUID only:
```
$ ./vacli fw-acl-list --ip-ref 5d6df920-39e1-447a-9dd6-e8bb2c621a01 --table +
idx action  protocol sourceIpv4Cidr sourcePorts destinationIpv4Cidr destinationPorts
 0   ACCEPT  TCP      0.0.0.0/0      0           xxx.151.224.200/32  443
 1   DISCARD ALL      0.0.0.0/0      0           xxx.151.224.200/32  0
```

Obviously, the resource UUID comprehension is a convenience, not a must. Therefore,
when unsure feel free to use HREFs.

You can use ```get-href``` command to comprehend resource instance or resource
type URLs by providing the corresponding UUID and resource type name, e.g.

```
# here we're resolving the HREF for the "tags" resource type
$ ./vacli get-href --type tags --table
https://amsa1.cloud.verizon.com/api/compute/tag/
# getting a HREF for the specific VM object
$ ./vacli get-href --type vms --id 346dd11b-307b-4798-8a9f-b5512a53fb22 --table
https://amsa1.cloud.verizon.com/api/compute/vm/346dd11b-307b-4798-8a9f-b5512a53fb22
```

In certain cases, however, it may be even more convenient to use native resource
name or notation instead of UUIDs. For example, it's easier to remember and use
IPs rather than their UUIDs, let alone HREFs:

```
$ ./vacli fw-acl-list --ip xxx.151.224.200 --table
idx action  protocol sourceIpv4Cidr sourcePorts destinationIpv4Cidr destinationPorts
 0   ACCEPT  TCP      0.0.0.0/0      0           xxx.151.224.200/32  443
 1   DISCARD ALL      0.0.0.0/0      0           xxx.151.224.200/32  0
```

The IP address is unique enough in this context to be used as the reference or
identifier by itself.

#### Going low level
If you're real API hacker and want to interact with REST APIs on the lowest level,
there is something here for you too. The VACLI provides corresponding commands for
the HTTP verbs: GET, POST, PUT, PATCH, DELETE and OPTIONS. You can even provide
your custom values to add or override HTTP request headers., e.g.
```
 ./vacli get --href https://services.enterprisecloud.terremark.com/cloudapi/ecloud/Time/ --headers accept:application/json x-tmrk-version:1.6
[
  {
    "CurrentServerTime": "/Date(1449664581047)/"
  }
]
```

### PROCESSING RESULTS
Following the Unix philosophy, which is favoring composability as opposed to a
monolithic design, the VACLI tool does not implement quering or filtering
facilities for the resulting JSON beyong the convenience feature allowing to
output JSON in a tabular format for further readability. There are number of
tools and utilities available, providing JSON query language or sophisticated
JSON filtering capabilities. If you're looking for such functionality, give
one of the following options a try:

1.  JMESPath is a XPath-like query language for JSON.
See http://jmespath.org and https://github.com/jmespath/jmespath.py

2.  Jq is a lightweight and flexible command-line JSON processor.
See http://stedolan.github.io/jq/


### FAQ
Why didn't you tell? Why didn't you ask? ;-)

#### Where do I get the access keys?
If you have access to the Cloud Console (aka Web UI), please proceed to the
'My Profile' -> 'API Keys' page. There you can create a pair of access and
secret keys and specify the level of access for the associated API user.
Otherwise, please contact your cloud-space or cloud account administrator
and request the keys from them.

#### Where can I find the corresponding API endpoint?
Each cloud instance may have a separate API endpoint URL. You can either
ask your account administrator or do some discovery on your own:
```
$ ./vacli get-resource-groups --table
name         href
US-NorthEast https://iadg2.cloud.verizon.com/api/compute/
US-Central   https://egwa1.cloud.verizon.com/api/compute/
US-West      https://sjca1.cloud.verizon.com/api/compute/
EU-North     https://amsa1.cloud.verizon.com/api/compute/
LATAM-East   https://grua1.cloud.verizon.com/api/compute/
EU-UK-North  https://uk5a1.cloud.verizon.com/api/compute/
```

#### Where can I find the account and the cloud-space IDs?
You can either ask your administrator or find out yourself, looking to the
full qualified resource ID.

For example, the following Resource Identified for the VM gives you all
details you may need:

    dc=vz-cloud,s=compute,c=US,l=iadb1,acct=1-12ABC33,cs=35fa...,type=vm,id=a6555c47...

    l    - your cloud instance (or location)
    acct - your account ID
    cs   - your cloud-space ID

#### I'm getting syntax errors. What's wrong?
If you're seeng something like below:
```
    ...
      File "vacli", line xxx
    headers = {k: v for k, v in (kv.split(':', 1) for kv in args.headers if ':' in kv)} if args.headers else None
                      ^
    SyntaxError: invalid syntax
```
The issue is, unfortunately, with syntax variations supported by different 
python versions. The error above is basically saying that the comprehension 
syntax is not supported in your python version. You need python 2.7.x.

#### The name is too long. Can I rename the VACLI tool?
Yes, you definitely can do this. The only thing to keep in mind - if you're 
using Bash shell auto-completion you may also need to change the vacli.bash 
script for auto-completion to work properly. There are no other dependencies.

#### Can I move .vacli config file elsewhere?
By default it's assumed that the config file is located in the same folder
as the VACLI tool itself. If you want to place the config file to a
different location you'll need to instruct the script on where to look for
configuration, e.g.
```
$ ./vacli --config-file ~/etc/.vacli get-root
```

#### I can see create-vm, but there is no corresponding delete-vm command. Do I miss something?
It's a valid question and the reason for not having per resource-type delete 
command is rather simple - the DELETE command is resource type agnostic and 
for resource removal you just use the `delete' command provided with a space 
separated list of HREFs corresponding to resources to be removed, e.g.
```
$ ./vacli delete --href href#1 href#2 href#3 ...
```

#### I'm getting socket error (8). What does it mean?
If you're getting the following error when trying to execute command -
"Got socket error (8) nodename nor servname provided, or not known",
the reason is most probably in no access to the API endpoint. In this
case you may need to use a proxy server. If you have a proxy in place,
please validate if it's working and allowing you to pass through it.

#### I'm getting an API Exception. Am I doing something wrong?
It's hard to say in general since issue may be really with API itself,
with the way how specific API call is made or, dare I say, with the script
itself :-) Please report this issue to maintainers (see SUPPORT section).
When submitting your question, please provide at least the 'info' or yet
better 'debug' log output. Just make sure you've removed all secret keys 
and other sensitive information. Having more details will help to reproduce 
and investigate your case quicker.

#### There is a feature/function I desperately need. Can you implement it?
As it's been already said in SUPPORT section, this code and the whole project 
provided as-is, as example code with no support commitment. Nonetheless, we'll 
definitely review your request and as time permits we may possibly implement a 
solution for you.

#### I'm a paranoid admin. Is is a good idea at all to provide API access to the end users? Can they zap the whole environment?
As they say - "with the great power comes great responsibility". In this case 
it's an admin's responsibility, not users'. This is to say, that the tool 
itself won't give the user more access than they get allocated by admin through 
the role assignment and RBAC and can already exercise in the Cloud Console 
(Web UI). For example, read-only API user won't be able to cause any harm even 
intentionally.

Saying that, the tool is definitely requiring some basic knowledge on the 
user's part and may be a good addition for power and advanced users toolkit.

#### Is this tool supported on Windows?
Yes, it is. The tool will work the same way on Windows as it works on other 
platforms. You need to be aware, though, about some Windows specifics, such 
as setting environment variables, etc... Unless you're using Cygwin, the 
shell auto-completion will not work on Windows, since it's a Bash shell 
feature.

#### Can I call the CLI tool from CRON or other script?
Yes, you can. The only caveat, you got to make sure that all required paths and
environment variables are set accordingly. You'll also need to make sure that 
the ```.vacli``` config file is found. You can either provide an absolute path 
via command-line option or yet better change current working dir to the script 
deployment location.

For example:
```
$ crontab -l
# API ping from CRON
* * * * *	/usr/bin/python /tmp/vacli/vacli --config-file /tmp/vacli/.vacli get-root >> /tmp/vacli/vacli.log 2>&1
```
or, more preferable way
```
# API ping from CRON
* * * * *	cd /tmp/vacli && /usr/bin/python vacli get-root >> vacli.log 2>&1
```

#### How do I find who has created certain objects?
Most resources have a "creator" property having additional details for the creator user and organization.

Here is an example for how you can fetch this information:
```
$ ./vacli get --href https://amsa1.cloud.verizon.com/api/compute/vdisk/?limit=2 --table id name size status creator.loginId creator.organization.name
id                                   name      size status creator.loginId                              creator.organization.name
b0ff50eb-9eb4-4164-a33b-f704b5f99460 Boot Disk 2048 ACTIVE apiuser/894140b8-6084-4337-b294-e93f5429b868 f43a0037-18c5-445f-bad0-abb34a06fa03
131abfe3-c626-44ff-a320-fad617b0a001 DELME     10   ACTIVE apiuser/894140b8-6084-4337-b294-e93f5429b868 f43a0037-18c5-445f-bad0-abb34a06fa03
```
