### SUMMARY

The `vacli' project has been inspired by awscli utility and provides similar
REST API access functionality for the VCC platform, also historically known
as project George or Vector A.

Below is the list of the most important features:

* self-sufficient, no external library or dependencies
* highly configurable (config file, env variables, CLI switches)
* supports multiple configuration profiles
* supports command line auto-completion
* advanced logging capabilities
* supports primitive HTTP commands
* significant REST API coverage
* supports both short (UUID) and long (HREF) resource IDs
* supports both JSON and tabular output formatting
* supports resource tags
* supports HTTP/HTTPS proxy

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
the Python version 2.7 only. Both Windows, Linux and MacOS versions were
tested.


### SETUP
There is no real setup required. The vacli is a python script working with both
Python 2.7. Unfortunately, earlier 2.4 and later versions 3.x are not supported
due to the syntax changes and compatibility constraints.

The tool does not depend on any external modules or libraries and may be used
right away as soon as you have your credentials and access point details setup.
The configuration options may be specified in several ways.

#### Configuration File .vacli
You can put your access and secret key as well as some additional parameters
into the .vacli configuration file, which is normally placed in the folder,
where vacli script resides. Shall you need to use configuration located elsewhere
make sure you added --config-file switch to tell where to look for settings

In the example below, the "default" subsection is a so called profile. You may 
define multiple profiles and switch between them using the --profile option. 
If no profile given, the "default" profile is used.
```
$ cat .vacli_example
{
   "default": {
     // optional proxy, can be removed for direct access to API endpoint
     "http_proxy": "proxy.....com:80",

     // the following are essential parameters defining your credentials
     "api_account": "720438c0-...",
     "api_cloud_space": "60f28e75-...",
     "api_access_key": "6451af2...",
     "api_secret_key": "RrIOESzok...",
     "api_endpoint": "https://amsa1.cloud.verizon.com"
   }
}

$ ./vacli --config-file /etc/vacli/vacli.cfg --profile default get-root

```

#### Shell Environment Variables
You can specify (override) all or some configuration parameters using the shell
environment variables. For example:

```
$ cat vacli.env

API_USER="john.doe@mail.com"
API_ORG="f43a0037-..."
API_ACCOUNT="720438c0-..."
API_CLOUD_SPACE="60f28e75-..."
API_ACCESS_KEY="6451af2..."
API_SECRET_KEY="RrIOESzok..."
API_ENDPOINT="https://amsa1.cloud.verizon.com"

export API_USER API_ORG API_ACCOUNT API_CLOUD_SPACE \
API_ACCESS_KEY API_SECRET_KEY API_ENDPOINT
```

#### Command Line Switches
Eventually, you can specify (override) all or some configuration parameters
using command line arguments. For example:

```
$ ./vacli --api-access-key="6451af2..." --api-secret-key="RrIOESzok..." get-root-master
```

Obviously, you can combine all three methods. In this case configuration file
values are overridden by environment variable, which are in turn overriden by
the command line options.

### USING PROXY
Sometimes egress HTTP/HTTPS calls are not allowed and the only way to access
the API endpoint is using HTTP proxy. Like other configuration settings the
proxy can be specified using either configuration file, environment variable
or corresponding command-line option, e.g.

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
Note: the SOCKS protocol is not supported.

### API PERFORMANCE AND CACHING
One of the REST API benefits - using HTTP protocol as its transport is at the
same quickly becoming one of its major shortcomings. Add SSL to the mix and the
proxy server in between and previously quick and responsive API calls all the
sudden becoming sluggish and slow. Now, run a loop to process hundreds API
calls and go get your favorite beverage.

Obviously, besides finding a quick and responsive proxy server not much can be
done to resolve the aforementioned issue. However, some little improvements
may be still achieved by caching some API call responses and reducing overall
chattiness.

#### Caching API calls
The caching itself may be good or evil, so special attention must be paid
to what is cached exactly and for how long. At the same time, caching
fairly immutable API responses must be safe enough and may help improving
API performance without sacrificing accuracy or reliability.

The VACLI does implement this idea and caches mostly immutable data in the
local file-system file: vacli.tmp. Normally, you don't need to care much
about this cache, clean or flush it, when moving to a different endpoint
or environment. It will be flushed or updated automatically.
```
$ ./vacli --log-level info list-vms --table
2015-10-05 12:13:14 INFO: RestClient.init(base_url: https://amsa1.cloud.verizon.com)
2015-10-05 12:13:14 INFO: RestClient.init(): reading API cache file vacli.tmp
```
... the line above tells that cache has been found and read successfully
```
2015-10-05 12:13:14 INFO: RestClient.get_href(group: vms, tag: None, ref: None)
2015-10-05 12:13:14 INFO: RestClient.get_root(tag: None)
2015-10-05 12:13:14 INFO: RestClient.get_root(): cache hit for href: https://amsa1.cloud.verizon.com/api/compute
```
... and here we can see that we saved one API call already by hitting the cache
```
2015-10-05 12:13:14 INFO: RestClient.request(verb: GET, url: https://amsa1.cloud.verizon.com/api/compute/vm/?limit=100)
2015-10-05 12:13:16 INFO: RestClient.request: TTFB: 2.151 sec, response read: 0.085 sec
```
... talking of performance, now the time to the first byte and for fetching response is measured as well
```
2015-10-05 12:13:16 INFO: RestClient.response: 200 OK
```

#### Decreasing API chattiness
As you may have seen from above example, there is a significant difference
between TTFB and response read times, poining back to the same issue -
protocol latency. Without diving deep and discussing more advance
optimization options, the long story short - the less the number of HTTP
request/response ping-pongs, the less overall API transaction time
is going to be. Employing caches may help to save on some API calls and
another improvement is coming from API feature allowing to fetch so called
"deep" JSON, where referenced objects are fully populated not a mere HREF
links.

The best it may be explained on example. Say we need to find all IPs
belonging to the given VM as well as information about all disks attached
to it. The usual approach is to:
- fetch VM objects (API call)
- for each VM fetch "vnics" collection (N x API calls)
- for each VM fetch "vdiskMounts" collection (N x API call)

It's easy to see that as number of VM grows, the number of required API
calls grows linearly along with it. Thus for 500 VMs, we're talking
about 1001 API calls at least.

The good news, starting from GOL 1.9.10, it's possible to pack it all into
a single API call, e.g.
```
$ ./vacli get --href https://iadb1.cloud.verizon.com/api/compute/vm/?expand=_item.vdiskMounts,_item.vnics
```

This single call will fetch "vnics" and "vdiskMounts" data and populate
corresponding JSON subtrees for every VM. Considering the TTFB time is
1 sec in average, the whole transaction that used to take 1000+ seconds
or 16+ min will take only couple seconds now.

### LOGGING AND DEBUGGING

#### Increasing output verbosity
You may want to increase verbosity to see specific API calls performed,
their inputs and output. For this, use the --log-level global option. The
"info" log-level does provide lot of details. The "debug" log-level goes
even further, providing raw HTTP request/response details.

#### Storing log messages to the file
If you don't want to clutter output with additional debug messaged, you can divert
them to the file by using --log-file option. By default STDOUT is used for the log
messages.
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
2015-06-12 12:52:53 INFO: RestClient.init(base_url: https://amsa1.cloud.verizon.com)
2015-06-12 12:52:53 INFO: RestClient.get_root(tag: None)
2015-06-12 12:52:53 INFO: RestClient.get(url: https://amsa1.cloud.verizon.com/api/compute)
2015-06-12 12:52:53 INFO: RestClient.request(verb: GET, url: https://amsa1.cloud.verizon.com/api/compute)
2015-06-12 12:52:54 INFO: RestClient.request(...).response: 200 OK
```

### AUTOCOMPLETION

#### Bash auto-completiong setup

If you want to enable Bash auto-completion, you have to source vacli.bash file, e.g.
```
$ . vacli.bash
```
Wasn't it easy?

#### Using Bash auto-completion
Just type ./vacli and press [TAB] twice. This will produce a list with available commands, e.g.
```
$ ./vacli <double TAB here>
delete                get-root-master       list-vnets            vdisk-create          vm-list-mounts
fw-acl-add            job-list              options               vdisk-edit            vm-list-vnics
fw-acl-del            job-wait              post                  vm-add-vdisk          vnet-create
fw-acl-list           list-vdisk-templates  public-ip-add         vm-add-vnic           vnet-edit
get                   list-vdisks           public-ip-del         vm-create             vnic-edit
get-admin-root        list-vm-templates     public-ip-list        vm-ctl
get-root              list-vms              update-iops           vm-edit
$ ./vacli
```

After typing a command you can either supply -h option and see additional help
for this particular command or enter -- and use double TAB to see options accepted
by this command, e.g.
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
id                                   operation          startTime      endTime        runTime progress status
ccf92856-0ccb-438f-85ae-29448d76857a POWER_ON_VM        05/20/15 11:06 05/20/15 11:07 47      100      FAILED
f6864969-790e-4d24-9d85-aee306a77b1b POWER_ON_VM        05/20/15 14:12 05/20/15 14:13 67      100      FAILED
ab54db1b-9674-460d-8665-b3c2f519e289 POWER_ON_VM        05/20/15 11:07 05/20/15 11:09 114     100      FAILED
51e8aa6e-4a6b-4778-938b-9692d50dfdbb ALLOCATE_IPADDRESS 05/21/15 15:28 05/21/15 15:28 0       100      COMPLETE
5534c86f-aad5-4f00-8d67-c5a7b7ad7880 POWER_ON_VM        06/01/15 21:10 06/01/15 21:12 110     100      FAILED
```

#### Some clever tricks
It's not all, there is some magic too! Let's imagine you want to list all firewall ACLs,
but you don't recall the IP assigned, let alone their assigned resource UUIDs...
Auto-completion is your friend, e.g.
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
All vacli commands normally producing a JSON output. You can use jq or jmespath to
query and filter resulting JSON and chain multiple calls using UNIX pipes. Sometimes,
however, it's more convenient to work with a tabular output. Most commands accepting
the --table option and printing certain JSON keys as a table columns. For example:
```
$ ./vacli public-ip-list
[
   {
     "address": "xxx.151.224.22",
     "creator": {
       "href": "https://amsa1.cloud.verizon.com/api/admin/user/d0f7f6c2-256b-4330-9a42-d3bfb82e94a0",
       "id": "d0f7f6c2-256b-4330-9a42-d3bfb82e94a0",
...

./vacli public-ip-list --with-vms --table
id                                   address         name      v  vm
12909981-7712-44aa-97a2-456bc92c1fb0 xxx.151.224.22  Public IP V4 https://amsa1.cloud.verizon.com/api/compute/vm/d5372f49-4df4-4d8a-8cbf-f39a3c85a48b
```

The --table option may also be instructed to produce the table with specific keys only,
instead of the default set, e.g.
```
$ ./vacli public-ip-list --table id address tags
id                                   address         tags
12909981-7712-44aa-97a2-456bc92c1fb0 xxx.151.224.22  []
```

#### Using Tags
The tags attached to various resource instances is a handy mechanism for grouping
resources and may be used by many commands to filter resources by specified tag, e.g.
```
$ ./vacli list-vms --tag api --table
id                                   status   os        name   description
30946c9a-a16a-489e-86ee-dc45f42a47d2 STARTING UBUNTU_64 DELME3 API Test
ad4b9ce1-0981-4cc6-890d-b3552fd7bd4c ON       UBUNTU_64 DELME2 API Test

$ ./vacli list-vms --tag win2012 --table
id                                   status os                     name        description
7047c7e9-b52f-4e4c-a2e4-2417036281e1 ON     WINDOWS_SERVER_2008_64 Test SQL 02 Test SQL 2012 AlwaysOn Server
7311df19-4fdf-45d3-83dd-050014c35311 ON     WINDOWS_SERVER_2012    winsvr02    Windows 2012 Server with SQL2012
889f7168-b47a-4b8c-bfc2-3cc36ef90653 ON     WINDOWS_SERVER_2008_64 Test SQL 03 Test SQL 2012 AlwaysOn Server
a6998a94-6c02-4f7b-95c9-6640dc31c3fc ON     WINDOWS_SERVER_2012    Test RDP GW RDP Gateway for TEST Domain
```

#### Referencing Objects
Every object in Verizon Cloud can be referenced by its URL or HREF and thus
all commands accepting HREFs. For example:
```
$ ./vacli list-vms --tag pfsense --table id name href
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

In most cases, when resource type is defined by the context, it's sufficient
to provide UUID only and complete HREF may be easily constructed on the fly.
In the example above we had to use HREF, since it's not clear from the context
what kind of resource we are requesting.

In the next example, using complete HREF is superfluous, since it's clear
that we're referencing IP address resource:
```
$ ./vacli fw-acl-list --ip-ref https://amsa1.cloud.verizon.com/api/compute/ip-address/5d6df920-39e1-447a-9dd6-e8bb2c621a01 --table
idx action  protocol sourceIpv4Cidr sourcePorts destinationIpv4Cidr destinationPorts
 0   ACCEPT  TCP      0.0.0.0/0      0           xxx.151.224.200/32  443
 1   DISCARD ALL      0.0.0.0/0      0           xxx.151.224.200/32  0
```

So, the same may be achived by using the resource UUID only:
```
$ ./vacli fw-acl-list --ip-ref 5d6df920-39e1-447a-9dd6-e8bb2c621a01 --table
idx action  protocol sourceIpv4Cidr sourcePorts destinationIpv4Cidr destinationPorts
 0   ACCEPT  TCP      0.0.0.0/0      0           xxx.151.224.200/32  443
 1   DISCARD ALL      0.0.0.0/0      0           xxx.151.224.200/32  0
```

Obviously, the resource UUID comprehension is a convenience, not must. Therefore,
when unsure feel free to use HREFs.

In certain cases, however, it may be even more convenient to use native resource
name or notation instead of UUIDs. For example, it's easier to remember and use
IPs rather than their UUIDs, let alone HREFs:

```
$ ./vacli fw-acl-list --ip xxx.151.224.200 --table
idx action  protocol sourceIpv4Cidr sourcePorts destinationIpv4Cidr destinationPorts
 0   ACCEPT  TCP      0.0.0.0/0      0           xxx.151.224.200/32  443
 1   DISCARD ALL      0.0.0.0/0      0           xxx.151.224.200/32  0
```

The IP address is unique enough to be used as the reference or identifier by itself.

#### Going low level
If you're real API hacker and want to interact with REST APIs on the lowest level,
there is something here for you too. The CLI provides corresponding commands for
the HTTP verbs: GET, POST, PUT, PATCH, DELETE and OPTIONS. You can even provide
your custom values to add or override HTTP request headers, e.g.
```
$ ./vacli get --href https://services.enterprisecloud.terremark.com/cloudapi/ecloud/Time/ --headers accept:application/json
[
   {
     "CurrentServerTime": "/Date(1435327578941)/"
   }
]
```

### PROCESSING RESULTS
Following the Unix philosophy, which is favoring composability as opposed to
monolithic design, the CLI tool does not implement quering or filtering
facilities for the resulting JSON beyong the convenience feature allowing to
output JSON in a tabular format for further readability. There are number of
tools and utilities available providing JSON query languge or sophisticated
JSON filtering capabilities. If you're looking for such functionality, give
one of the following options a try:

1.  JMESPath is a XPath-like query language for JSON.
See http://jmespath.org and https://github.com/jmespath/jmespath.py

2.  Jq is a lightweight and flexible command-line JSON processor.
See http://stedolan.github.io/jq/


### FAQ
Why didn't you tell? Why didn't you ask? :)

#### Where do I get the access keys?
If you have access to the Cloud Console (aka Web UI), please proceed to the
'My Profile' -> 'API Keys' page. There you can create a pair of access and
secret keys and specify the level access for the associated API user.
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
full qualified resource ID in the Cloud Console (Web UI).

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
The issue is, unfortunately, with syntax, namely with various syntax
variations supported by different python versions. The error above is
basically saying that the comprehension syntax is not supported in your
python version. You need python 2.7 at least.

#### The name is too long. Can I rename the `vacli' script?
Yes, you definitely can do this. The only thing to keep in mind - you
may also need to change the script name in the vacli.bash script in
case if you use shell auto-completion, otherwise, there are no other
dependencies.

#### Can I move .vacli config file elsewhere?
By default it's assumed that the config file is located in the same folder
as the `vacli' script itself. If you want to place the config file to a
different location you'll need to instruct the script on where to look for
configuration, e.g.
```
$ ./vacli --config-file ~/etc/.vacli get-root
```

#### I can see create-vm, but there is no corresponding delete-vm command. Did I miss something?
It's a valid question and the reason for not having per resource-type
delete command is rather simple - the DELETE command is resource type
agnostic and for resource removal you just use the `delete' command
provided with space separated list of resource HREFs, e.g.
```
$ ./vacli delete --href href#1 href#2 href#3 ...
```
#### I'm getting socket error (8). What does it mean?
If you're getting the following error when trying to execute command -
"Got socket error (8) nodename nor servname provided, or not known",
the reason is most probably in no access to the API endpoint. In this
case you may need to use a proxy server. If you have proxy in place,
please validate if it's working and allowing you to pass through it.

#### I'm getting an API Exception. Am I doing something wrong?
It's hard to say in general since issue may be really with API itself,
with the way how specific API call is made or, dare I say, with the script
itself :) Please report this issue to maintainers (see SUPPORT section).
When submitting your question, please provide at least the `info' or yet
better `debug' log output (just make sure you've removed all keys and other
sensitive information). Having more details will help to reproduce and
investigate your case.

#### There is a feature/function I desperately need. Can you implement it?
As it's been already said in SUPPORT section, this code and the whole
project provided as-is, as example code with no support committment.
Nonetheless, we'll definitely review your request and as time permits
we may possibly have a solution for you.

#### I'm a paranoid admin. Is is a good idea at all to provide API access to the end users? Can they zap the whole environment?
As they say - "with the great power comes great responsibility". In this
case it's an admin's responsibility, not users'. This is to say, that the
tool itself won't give the user more access than they get allocated by
admin (through the role assignment and RBAC) and can already exercise
in the Cloud Console (Web UI). For example, read-only API user won't be
able to cause any harm even intentionally.

Saying that, the tool is definitely requiring some basic knowledge on
the user's part and may be a good addition for power and advanced users
toolkit.

#### Is this tool supported on Windows?
Yes, it is. The tool will work the same way on Windows as it works on
other platforms. Actually, it's a Python feature. You need to be aware,
though, about some Windows specifics as setting environment variables,
etc... Unless you're using Cygwin, the shell auto-completion will not
work on Windows, since it's a Bash shell feature.

#### Can I call the CLI tool from CRON or other script?
Yes, you can. The only caveat, you got to make sure that all required
paths and environment variables are set accordingly. You'll also need
to make sure that .vacli config is found. You can either provide an
absolute path via command-line option or yet better change current
working dir to the script deployment location.

For example:
```
$ crontab -l
# API ping from CRON
* * * * *	/usr/bin/python /tmp/vacli/vacli --config-file /tmp/vacli/.vacli get-root >> /tmp/vacli/vacli.log 2>&1
```
or, more preferrable way
```
# API ping from CRON
* * * * *	cd /tmp/vacli && /usr/bin/python vacli get-root >> vacli.log 2>&1
```
