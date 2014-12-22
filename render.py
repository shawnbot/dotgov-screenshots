import argparse

parser = argparse.ArgumentParser(
    description="Render some screenshots of government web sites!")
parser.add_argument("filename",
    help="the CSV to read (assumed to have a 'Domain Name' column)")
parser.add_argument("outdir",
    help="where to write the PNGs")
parser.add_argument("--width", dest="width", type=int,
    default=960,
    help="Page width in pixels (default: 960)")
parser.add_argument("--scale", dest="scale", type=float,
    default=.125,
    help="Thumbnail scale as a decimal fraction (default: .125)")
args = parser.parse_args()

import sys, os, shutil
import csv, subprocess

infile = args.filename
outdir = args.outdir
stream = open(infile, "r")

missing = "../meta/missing-full.png"

thumb_type = "thumb"
thumb_size = args.width * args.scale

for row in csv.DictReader(stream, dialect="excel"):
    domain = row["Domain Name"]
    outfile = os.path.join(outdir, "%s-full.png" % domain)

    if os.path.exists(outfile):
        print "skipping: %s" % outfile
        continue

    print "rendering: %s" % outfile
    returncode = subprocess.call([
        "time", # time it!
        # render full size
        "webkit2png", "-F",
        # and thumbnails
        (thumb_type == "clipped" and "-C" or "-T"),
        # set the viewport size
        "--width", str(args.width),
        # thumbnail scale
        "--scale", str(args.scale),
        # clipped thumbnail size
        "--clipwidth", str(thumb_size),
        "--clipheight", str(thumb_size),
        # put them in this directory
        "--dir", outdir,
        # name them "{domain}-{full,clipped}.png"
        "-o", domain,
        "http://%s" % domain.lower()
    ], stdout=sys.stdout, stderr=sys.stderr)

    if returncode == 1 or not os.path.exists(outfile):
        print "*** failed to render: %s" % outfile
        os.symlink(missing, outfile)
        os.symlink(*map(lambda f: f.replace("-full", "-%s" % thumb_type), (missing, outfile)))

stream.close()
