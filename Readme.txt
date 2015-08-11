
SETUP

There is no real setup required. The vacli is a python script working with both
Python 2.x and 3.x versions. It does not depend on any external modules and may
be used right away as soon as you have got your access keys.

The configuration options may be specified in several ways:

1.  You can put your access and secret key as well as some additional parameters
    into the .vacli configuration file, which is normally placed in the folder,
    where vacli script resides. For example:

    $ cat .vacli

    {
      "default": {
        "api_user": "vyacheslav.vladyshevsky@intl.verizon.com",
        "api_org": "f43a0037-...",
        "api_account": "720438c0-...",
        "api_cloud_space": "60f28e75-...",
        "api_access_key": "6451af2...",
        "api_secret_key": "RrIOESzok...",
        "api_endpoint": "https://amsa1.cloud.verizon.com"
      }
    }

    In this example above, the "default" subsection is a so called profile. You
    may define multiple profiles and switch between them using the --profile
    option, e.g.

    $ ./vacli --profile qa get-root

    If profile is not specified, the "default" profile is assumed.

2.  You can specify (override) all or some configuration parameters using shell
    environment variables. For example:

    $ cat vacli.env

    API_USER="vyacheslav.vladyshevsky@intl.verizon.com"
    API_ORG="f43a0037-..."
    API_ACCOUNT="720438c0-..."
    API_CLOUD_SPACE="60f28e75-...",
    API_ACCESS_KEY="6451af2..."
    API_SECRET_KEY="RrIOESzok...",
    API_ENDPOINT="https://amsa1.cloud.verizon.com"

    export API_USER API_ORG API_ACCOUNT API_CLOUD_SPACE \
    API_ACCESS_KEY API_SECRET_KEY API_ENDPOINT

3.  Eventually, you can specify (override) all or some configuration parameters
    using command line arguments. For example:

    $ ./vacli --api-access-key="6451af2..." --api-secret-key="RrIOESzok..." get-root-master

    Obviously, you can combine all three methods. In this case configuration file
    values are overridden by environment variable, which are in turn overriden by
    the command line options


LOGGING AND DEBUGGING

1.  Increasing output verbosity
    You may want to increase verbosity to see specific API calls performed, their
    inputs and output. For this, use the --log-level global option. The `info' log-level
    does provide lot of details. The `debug' log-level goes even further, providing
    raw HTTP request/response details.

2.  Storing log messages to the file
    If you don't want to clutter output with additional debug messaged, you can divert
    them to the file by using --log-file option. By default STDOUT is used for the log
    messages.

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


AUTOCOMPLETION

1.  Bash auto-completiong setup

    If you want to enable Bash auto-completion, you have to source vacli.bash file, e.g.

    $ . vacli.bash

    Wasn't it easy?

2.  Using Bash auto-completion

    Just type ./vacli and press <TAB> twice. This will produce a list with available commands, e.g.

    $ ./vacli <double TAB here>
    delete                get-root-master       list-vnets            vdisk-create          vm-list-mounts
    fw-acl-add            job-list              options               vdisk-edit            vm-list-vnics
    fw-acl-del            job-wait              post                  vm-add-vdisk          vnet-create
    fw-acl-list           list-vdisk-templates  public-ip-add         vm-add-vnic           vnet-edit
    get                   list-vdisks           public-ip-del         vm-create             vnic-edit
    get-admin-root        list-vm-templates     public-ip-list        vm-ctl
    get-root              list-vms              update-iops           vm-edit
    $ ./vacli

    After typing a command you can either supply -h option and see additional help
    for this particular command or enter -- and use double TAB to see options accepted
    by this command, e.g.

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

3.  Some clever tricks

    It's not all, there is some magic too! Let's imagine you want to list all firewall ACLs,
    but you don't recall the IP assigned, let alone their assigned resource UUIDs...
    Auto-completion is your friend, e.g.

    $ ./vacli fw-acl-list --ip <double TAB here>
    204.151.224.199  204.151.224.2    204.151.224.200  204.151.224.22   204.151.224.99   204.151.225.0    204.151.225.100
    $ ./vacli fw-acl-list --ip 204.151.22

    Furthermore, all command-line switches accepting values from a predefined set, can
    generate hints and auto-complete your input, e.g.

    $ ./vacli --log-level <double TAB>
    critical  debug     error     info      warning

    $ ./vacli fw-acl-add --<double TAB>
    --action    --dst-cidr  --idx       --ip-ref    --src-cidr
    --dry-run   --dst-port  --ip        --proto     --src-port

    $ ./vacli fw-acl-add --action <double TAB>
    ACCEPT   DISCARD  REJECT

    $ ./vacli fw-acl-add --action DISCARD --proto <double TAB>
    ALL   ESP   ICMP  TCP   UDP

    and so on...


USAGE EXAMPLES

1.  Formatting Output

    All vacli commands normally producing a JSON output. You can use jq or jmespath to
    query and filter resulting JSON and chain multiple calls using UNIX pipes. Sometimes,
    however, it's more convenient to work with a tabular output. Most commands accepting
    the --table option and printing certain JSON keys as a table columns. For example:

    $ ./vacli public-ip-list
    [
      {
        "address": "204.151.224.22",
        "creator": {
          "href": "https://amsa1.cloud.verizon.com/api/admin/user/d0f7f6c2-256b-4330-9a42-d3bfb82e94a0",
          "id": "d0f7f6c2-256b-4330-9a42-d3bfb82e94a0",
    ...

    ./vacli public-ip-list --with-vms --table
    id                                   address         name      v  vm
    12909981-7712-44aa-97a2-456bc92c1fb0 204.151.224.22  Public IP V4 https://amsa1.cloud.verizon.com/api/compute/vm/d5372f49-4df4-4d8a-8cbf-f39a3c85a48b

    The --table option may also be instructed to produce the table with specific keys only,
    instead of the default set, e.g.

    $ ./vacli public-ip-list --table id address tags
    id                                   address         tags
    12909981-7712-44aa-97a2-456bc92c1fb0 204.151.224.22  []
    ...


2.  Using Tags

    The tags attached to various resource instances is a handy mechanism for grouping
    resources and may be used by many commands to filter resources by specified tag, e.g.

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

3.  Referencing Objects

    Every object in Verizon Cloud can be referenced by its URL or HREF and thus
    all commands accepting HREFs. For example:

    $ ./vacli list-vms --tag pfsense --table id name href
    id                                   name     href
    d5372f49-4df4-4d8a-8cbf-f39a3c85a48b fw-auto  https://amsa1.cloud.verizon.com/api/compute/vm/d5372f49-4df4-4d8a-8cbf-f39a3c85a48b
    ac633b5d-7675-4f49-b558-ee34d9ae3825 test-fw  https://amsa1.cloud.verizon.com/api/compute/vm/ac633b5d-7675-4f49-b558-ee34d9ae3825
    3d7406f5-9206-4419-84cc-cd2f4ea924c2 front-fw https://amsa1.cloud.verizon.com/api/compute/vm/3d7406f5-9206-4419-84cc-cd2f4ea924c2

    As you can see, the HREF includes both:
    - API endpoint: https://amsa1.cloud.verizon.com
    - API root: /api/compute
    - resource type: /vm
    - resource UUID: d5372f49-4df4-4d8a-8cbf-f39a3c85a48b

    $ ./vacli get --href https://amsa1.cloud.verizon.com/api/compute/vm/d5372f49-4df4-4d8a-8cbf-f39a3c85a48b
    [
      {
        "arch": "x86_64",
        "consoleHref": ...

    In most cases, when resource type is defined by the context, it's sufficient
    to provide UUID only and complete HREF may be easily constructed on the fly.
    In the example above we had to use HREF, since it's not clear from the context
    what kind of resource we are requesting.

    In the next example, using complete HREF is superfluous, since it's clear
    that we're referencing IP address resource:

    $ ./vacli fw-acl-list --ip-ref https://amsa1.cloud.verizon.com/api/compute/ip-address/5d6df920-39e1-447a-9dd6-e8bb2c621a01 --table
    idx action  protocol sourceIpv4Cidr sourcePorts destinationIpv4Cidr destinationPorts
    0   ACCEPT  TCP      0.0.0.0/0      0           204.151.224.200/32  443
    1   DISCARD ALL      0.0.0.0/0      0           204.151.224.200/32  0

    So, the same may be achived by using the resource UUID only:

    $ ./vacli fw-acl-list --ip-ref 5d6df920-39e1-447a-9dd6-e8bb2c621a01 --table
    idx action  protocol sourceIpv4Cidr sourcePorts destinationIpv4Cidr destinationPorts
    0   ACCEPT  TCP      0.0.0.0/0      0           204.151.224.200/32  443
    1   DISCARD ALL      0.0.0.0/0      0           204.151.224.200/32  0

    Obviously, the resource UUID comprehension is a convenience, not must. Therefore,
    when unsure feel free to use HREFs.

    In certain cases, however, it may be even more convenient to use native resource
    name or notation instead of UUIDs. For example, it's easier to remember and use
    IPs rather than their UUIDs, let alone HREFs:

    $ ./vacli fw-acl-list --ip 204.151.224.200 --table
    idx action  protocol sourceIpv4Cidr sourcePorts destinationIpv4Cidr destinationPorts
    0   ACCEPT  TCP      0.0.0.0/0      0           204.151.224.200/32  443
    1   DISCARD ALL      0.0.0.0/0      0           204.151.224.200/32  0

    The IP address is unique enough to be used as the reference or identifier by itself.

4.  Going low level

    If you're real API hacker and want to interact with REST APIs on the lowest level,
    there is something here for you too. The CLI provides corresponding commands for
    the HTTP verbs: GET, POST, PUT, PATCH, DELETE and OPTIONS. You can even provide
    your custom values to add or override HTTP request headers, e.g.

    $ ./vacli get --href https://services.enterprisecloud.terremark.com/cloudapi/ecloud/Time/ --headers accept:application/json
    [
      {
        "CurrentServerTime": "/Date(1435327578941)/"
      }
    ]


PROCESSING RESULTS

Following the Unix philosophy, which is favoring composability as opposed to
monolithic design, the CLI tool does not implement quering or filtering
facilities for the resulting JSON beyong the convenience feature allowing to
output JSON in a tabular format for further readability. There are number of
tools and utilities available providing JSON query languge or sophisticated
JSON filtering capabilities. If you're looking for such functionality, give
one of the following options a try:

1.  JMESPath is a XPath-like query language for JSON.
    http://jmespath.org
    https://github.com/jmespath/jmespath.py

2.  Jq is a lightweight and flexible command-line JSON processor.
    http://stedolan.github.io/jq/
