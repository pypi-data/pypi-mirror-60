#!/usr/bin/env python3
# © 2019-2020 Vidmantas Balčytis

import  sys
from    lieparse        import  lieParser, VarsClass
from    urllib.request  import  Request, urlopen
from    ssl             import create_default_context, CERT_NONE
from    argparse        import  ArgumentParser
from    os              import path
import  re
import pkg_resources


Version = pkg_resources.get_distribution("lieparse").version

usragents = {
    "chrome" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "firefox" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0",
    "edge" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363",
    "explorer" : "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "ga_tabS2" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.93 Safari/537.36",
    "ga_phs7"  : "Mozilla/5.0 (Linux; Android 8.0.0; SM-G930F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.93 Mobile Safari/537.36",
}
defusragent = "chrome"

def err_exit(msg):
    print("ERROR:", msg, file=sys.stderr)
    exit(1)

def verbose(msg):
    if args.v:
        print(msg, file=sys.stderr)

#---------------- Main entry ---------------------
def main():
    global args
    parser = ArgumentParser(description="""HTML parser ant text retriever using user defined rule set.
    © 2019-2020 Vidmantas Balčytis
    """)


    parser.add_argument('--get-samples', action='store_true', help="Install sample files into current directory")
    #parser.add_argument('--cookie', metavar='string', help="Send cookie")
    #parser.add_argument('--cookie-file', metavar='filename', help="Send cookie from file")
    parser.add_argument('--agent', metavar='agent name', help="Specify user agent name to use")
    parser.add_argument('--list-agents', action='store_true', help="List agents available internaly")
    parser.add_argument('--agent-file', metavar='filename', help="Get agent from file")
    parser.add_argument('--url', metavar='URL', help="Specify URL to get data from")
    parser.add_argument('--url-file', metavar='filename', help="Read URL from specified file")
    parser.add_argument('--from-url', metavar='URL', help="Optionaly specify URL from which we are comming")
    parser.add_argument('--from-url-file', metavar='URL', help="Read URL from which we are comming from file")
    parser.add_argument('--rule', metavar='rule', help="Specify rules inline")
    parser.add_argument('--rule-file', metavar='filename', help="Read rules from specified file")
    parser.add_argument('--ssl-verify', action='store_true', help="Verify site certificate. Defaults to false.")
    parser.add_argument('--dump-rules', action='store_true', help="Dump compiled rules")
    parser.add_argument('--dump-vars', action='store_true', help="Dump all variables")
    parser.add_argument('--dump-json', action='store_true', help="Dump all variables as JSON")
    parser.add_argument('--dump-json-np', action='store_true', help="Dump all variables as JSON, no prety-print")
    parser.add_argument('--write-html', metavar='filename', help="Write retrieve HTML dtat to file")
    parser.add_argument('-o', '--output-file', metavar='filename', help="Write results to file instaed of stdout")
    parser.add_argument('-i', metavar='data directory', default=".", help="Get values from here. Recognized filenames are rule.txt, url.txt, from_url.txt, usragent.txt") #, cookie.txt")
    parser.add_argument('-v', action='store_true', help="Be verbose")
    parser.add_argument('-V', action='store_true', help="Print version")
    args = parser.parse_args()

    if args.V:
        print("LiepaParse version {}".format(Version))
        exit(0)

    if args.get_samples:
        import tarfile
        fn = pkg_resources.resource_filename("lieparse.samples", "samples.tar.gz")
        with tarfile.open(fn) as f:
            f.extractall()
        exit(0)

    if args.list_agents:
        print("Known user agents:", " ".join([n for n in usragents]))
        exit(0)

    Dir = path.abspath(args.i)
    dfile = path.join(Dir, "url.txt")
    if not path.isdir(Dir):
        err_exit("specified location {} is not a directory".format(args.i))

    dfile = path.join(Dir, "url.txt")
    if args.url is not None:
        url = args.url
        verbose("Using user specified URL {}".format(url))
    elif args.url_file is not None:
        if not path.isfile(args.url_file):
            err_exit("cannot find URL file {}".format(args.url_file))
        with open(args.url_file, encoding = "utf-8") as f:
            url = f.read().strip()
        verbose("Using user specified URL from file {}: {}".format(args.url_file, url))
    elif path.isfile(dfile):
        with open(dfile, encoding = "utf-8") as f:
            url = f.read().strip()
        verbose("Using URL from file {}: {}".format(dfile, url))
    else:
        err_exit("URL must be specified")

    dfile = path.join(Dir, "from_url.txt")
    from_url = None
    if args.from_url is not None:
        from_url = args.from_url
        verbose("Using user specified previous host URL {}".format(from_url))
    elif args.from_url_file is not None:
        if not path.isfile(args.from_url_file):
            err_exit("cannot find FROM_URL file {}".format(args.from_url_file))
        with open(args.from_url_file, encoding = "utf-8") as f:
            from_url = f.read().strip()
        verbose("Using user specified FROM URL from file {}: {}".format(args.url_file, url))
    elif path.isfile(dfile):
        with open(dfile, encoding = "utf-8") as f:
            url = f.read().strip()
        verbose("Using FROM URL from file {}: {}".format(dfile, url))

    dfile = path.join(Dir, "rule.txt")
    if args.rule is not None:
        rules = args.rule
        verbose("Using user defined RULE {}".format(dfile, rules))
    elif args.rule_file is not None:
        if not path.isfile(args.rule_file):
            err_exit("cannot find rules file {}".format(args.rule_file))
        with open(args.rule_file, encoding = "utf-8") as f:
            rules = f.read()
        verbose("Using RULES from file {}: {}".format(args.rule_file, rules))
    elif path.isfile(dfile):
        with open(dfile, encoding = "utf-8") as f:
            rules = f.read()
        verbose("Using RULES from file {}: {}".format(dfile, rules))
    else:
        err_exit("RULE must be specified")

    dfile = path.join(Dir, "usragent.txt")
    if args.agent is not None:
        if args.agent not in usragents:
            err_exit("unknown user agent {}. To get list of known agents use --list-agents")
        usragent = usragents[args.agent]
        verbose("Using user specified USRAGENT {}: {}".format(args.agent, usragent))
    elif args.agent_file is not None:
        if not path.isfile(args.agent_file):
            err_exit("cannot find usragents file {}".format(args.agent_file))
        with open(args.agent_file, encoding = "utf-8") as f:
            usragent = f.read().strip()
        verbose("Using USRAGENT from file {}: {}".format(args.agent_file, usragent))
    elif path.isfile(dfile):
        with open(dfile, encoding = "utf-8") as f:
            usragent = f.read().strip()
        verbose("Using USRAGENT from file {}: {}".format(dfile, usragent))
    else:
        usragent = usragents[defusragent]
        verbose("Using default USRAGENT {}: {}".format(defusragent, usragent))

    # cookie = None
    # dfile = path.join(Dir, "cookie.txt")
    # if args.cookie is not None:
    #     cookie = args.cookie
    #     verbose("Using user specified COOKIE {}".format(cookie))
    # elif args.cookie_file is not None:
    #     if not path.isfile(args.cookie_file):
    #         err_exit("cannot find COOKIE file {}".format(args.cookie_file))
    #     with open(args.cookie_file, encoding = "utf-8") as f:
    #         cookie = f.read().strip()
    #     verbose("Using COOKIE from file {}: {}".format(args.cookie_file, cookie))
    # elif path.isfile(dfile):
    #     with open(dfile, encoding = "utf-8") as f:
    #         cookie = f.read().strip()
    #     verbose("Using COOKIE from file {}: {}".format(dfile, cookie))

    parser = lieParser(rules)
    if args.dump_rules:
        parser.synparser.printTree()
        exit(0)


    rq = Request(url,
                headers = {b"User-Agent" : usragent.encode()},
                origin_req_host = args.from_url)

    # if cookie is not None:
    #     c.setopt(c.COOKIE, cookie)

    re_charset5 = re.compile(rb'<\s*meta\s+charset="(.*?)"\s*>', re.I)
    re_charset = re.compile(rb'<\s*meta\s+http-equiv="Content-Type"\s+content="text/html;\s*charset=(.*?)"\s*>', re.I)
    enc = "utf-8"           # Default, if meta is not found
    if rq:
        ctx = None
        if not args.ssl_verify:
            ctx = create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = CERT_NONE
        with urlopen(rq, context = ctx) as f:
            hd = f.read()                       # FIXME: cannot read partial buffer, because can have end in the middle of utf-8 character
            m = re_charset5.search(hd)
            if m is None:
                m = re_charset.search(hd)
            if m is not None:
                enc = m.group(1).decode("utf-8").strip().lower()
            s = hd.decode(enc)

    if args.write_html is not None:
        with open(args.write_html, mode="w", encoding = "utf-8") as f:
            f.write(s)

    of = None
    if args.output_file is not None:
        of = open(args.output_file, mode="w", encoding = "utf-8")

    if of is not None:
        parser.setOutfile(of)

    parser.feed(s)
    v = parser.close()

    if of is not None:
        of.close()

    if v != 0:
        print("Unmatched {} items".format(v), file=sys.stderr)

    if args.dump_vars or args.dump_json or args.dump_json_np:
        va = VarsClass()
        va.count(parser.synparser.counter)
        if args.dump_vars:
            print(file=sys.stderr)
            print('*'*30, "Variable Dump", '*'*30, file=sys.stderr)
            va.dump()
            print('*'*26, "End of variable Dump", '*'*27, file=sys.stderr)
        if args.dump_json:
            va.dump_json(pp = True)
        if args.dump_json_np:
            va.dump_json()
