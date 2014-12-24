#!/usr/bin/env python
import os, sys
import urllib
import unicodecsv as csv
import url2png

import argparse
import utils

parser = argparse.ArgumentParser(
    description="""
Read domain names from a CSV file (or stdin), take screenshots of
them, and write the results to CSV.

You must provide a url2png API key (--key | -K) and secret (--secret
| -S). You can alternatively set the URL2PNG_KEY and/or
URL2PNG_SECRET environment variables.
""")
parser.add_argument("INPUT",
    type=utils.readfile("rU"),
    default=sys.stdin,
    help="the CSV file from which to load domains")
parser.add_argument("--key", "-K", dest="api_key",
    default=os.environ.get("URL2PNG_KEY"),
    help="your url2png API key (default: $URL2PNG_KEY)")
parser.add_argument("--secret", "-S", dest="api_secret",
    default=os.environ.get("URL2PNG_SECRET"),
    help="your url2png API secret (default: $URL2PNG_SECRET) ")
parser.add_argument("--column", "-c", dest="column",
    default="Domain Name",
    help="the column from which to read domain names in the CSV input (default: '%(default)s')")
parser.add_argument("--size", "-s", dest="size",
    default="1024x768",
    help="the viewport size, in the form 'WxH' (default: '%(default)s')")
parser.add_argument("--dir", "-d", dest="outdir",
    default=None, # the default is actually the cwd
    help="the directory into which screenshots should be written")
parser.add_argument("--output", "-o", dest="output",
    type=utils.writefile("w"),
    default=sys.stdout,
    help="the filename of the CSV output")
parser.add_argument("--full", "-F", dest="fullpage",
    action="store_true",
    default=None,
    help="capture the full page height (default: only capture the viewport)")
parser.add_argument("--thumb", "-t", dest="thumb",
    type=int,
    help="the max thumbnail width, in pixels")
parser.add_argument("--wait", "-w", dest="wait",
    action="store_true",
    default=None,
    help="wait for the document to be fully loaded (?) before taking a screenshot")
parser.add_argument("--ttl", dest="ttl",
    type=int,
    help="the screenshot time to live, in seconds")
args = parser.parse_args()

if not args.api_key or not args.api_secret:
    parser.print_help()
    sys.exit(1)

# create the API instance
api = url2png.API(key=args.api_key, secret=args.api_secret)
# generate request parameters from the parsed arguments
params = api.make_params(args)

print >> sys.stderr, "request parameters: %s" % params

csv_in = args.INPUT
reader = csv.DictReader(csv_in)
writer = None
csv_out = args.output

outdir = (args.outdir and args.outdir or ".")

try:
    for row in reader:
        domain = row["Domain Name"].lower()
        url = "http://%s" % domain
        req = api.capture(url, params)
        if req:
            if req["status"] == url2png.OK:
                outfile = os.path.join(outdir, "%s.png" % domain)
                urllib.urlretrieve(req["png"], outfile)
                row["image"] = outfile
            row["status"] = req["status"]
        else:
            row["status"] = "error"

        if row.get("image"):
            print >> sys.stderr, "+ captured: %s -> %s" % (domain, row["image"])
        else:
            print >> sys.stderr, "- error: %s" % domain

        if not writer:
            fieldnames = list(reader.fieldnames)
            fieldnames = fieldnames + ["status", "image"]
            # print >> sys.stderr, "* writing field names: %s" % fieldnames
            writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
            writer.writeheader()
        writer.writerow(row)
except KeyboardInterrupt:
    csv_out.close()
    sys.exit(1)

csv_out.close()
