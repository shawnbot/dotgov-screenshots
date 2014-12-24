from selenium import webdriver
from selenium.common.exceptions import *

import os, sys
import urllib
import unicodecsv as csv

browser = webdriver.Firefox()
browser.set_window_size(1024, 960)
browser.set_page_load_timeout(10)

outdir = "screenshots"
if not os.path.exists(outdir):
    print >> sys.stderr, "+ making outdir: %s" % outdir
    os.makedirs(outdir)

csv_in = urllib.urlopen("https://gsa.github.io/data/dotgov-domains/2014-12-01-full.csv")
reader = csv.DictReader(csv_in)

csv_out = open(os.path.join(outdir, "status.csv"), "w")
writer = None

failed = 0
give_up_after = 10

def cleanup():
    csv_out.close()
    browser.quit()

try: 
    for row in reader:
        domain = row["Domain Name"]
        url = "http://%s" % domain.lower()
        outfile = os.path.join(outdir, "%s.png" % domain)

        print >> sys.stderr, "* loading: %s ..." % url
        try:
            browser.get(url)
        except TimeoutException:
            print >> sys.stderr, "x (timed out: %s)" % url
            row["status"] = 500
            row["title"] = "(timed out)"
            failed = failed + 1
        except:
            print >> sys.stderr, "* unable to fetch: %s" % url
            row["status"] = 404
            failed = failed + 1

        if failed == give_up_after:
            print >> sys.stderr, "* failed %d times in a row; giving up!" % failed
            break

        print >> sys.stderr, "+ capturing: %s ..." % outfile
        try:
            browser.get_screenshot_as_file(os.path.abspath(outfile))
            print >> sys.stderr, "  captured."
            row["status"] = 200
            row["image"] = outfile
            row["title"] = browser.title
            failed = 0
        except:
            print >> sys.stderr, "x (unable to capture: %s)" % url
            row["status"] = 500

        # "leave" the current page
        browser.get("about:blank")

        if not writer:
            fieldnames = list(reader.fieldnames)
            fieldnames = fieldnames + ["status", "image", "title"]
            # print >> sys.stderr, "* writing field names: %s" % fieldnames
            writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
            writer.writeheader()

        # print >> sys.stderr, "writing: %s" % row
        writer.writerow(row)

except KeyboardInterrupt:
    cleanup()

cleanup()
