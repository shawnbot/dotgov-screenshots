# .gov screenshots

This repo grabs [.gov domain names](https://18f.gsa.gov/2014/12/18/a-complete-list-of-gov-domains/) and
generates screenshots of each site using [url2png](http://www.url2png.com/), a [paid service](https://www.url2png.com/plans/) with a [dead-simple API](https://www.url2png.com/docs/) that caches the results on Amazon S3.

## Taking screenshots
1. Make sure you have GNU Make and Python.
2. Create an account with [url2png](http://www.url2png.com/) and get your API key and secret from the [dashboard](http://www.url2png.com/dashboard/).
3. Set the `URL2PNG_KEY` and `URL2PNG_SECRET` environment variables, e.g.:
  
    ```sh
    $ export URL2PNG_KEY="PXXXXXXX"
    $ export URL2PNG_SECRET="SXXXXXX"
    ```
4. Run `make` to generate the `screenshots` directory.
5. When it's finished (or after enough captures have completed for `screenshots/status.csv` to have some text in it), open `index.html` to view the screenshots. **Note:** You'll need to do this in Apache
or using another webserver (e.g. `python -m SimpleHTTPServer`) because browsers disable XHR
requests from `file:///` URLs.

## capture.py
The included `capture.py` also serves as a general-purpose command line tool for generating screenshots from any CSV file containg domain names in one of its columns.

```
usage: capture.py [-h] [--key API_KEY] [--secret API_SECRET] [--column COLUMN]
                  [--size SIZE] [--dir OUTDIR] [--output OUTPUT] [--full]
                  [--thumb THUMB] [--wait] [--ttl TTL]
                  INPUT

Read domain names from a CSV file (or stdin), take screenshots of them, and
write the results to CSV. You must provide a url2png API key (--key | -K) and
secret (--secret | -S). You can alternatively set the URL2PNG_KEY and/or
URL2PNG_SECRET environment variables.

positional arguments:
  INPUT                 the CSV file from which to load domains

optional arguments:
  -h, --help            show this help message and exit
  --key API_KEY, -K API_KEY
                        your url2png API key (default: $URL2PNG_KEY)
  --secret API_SECRET, -S API_SECRET
                        your url2png API secret (default: $URL2PNG_SECRET)
  --column COLUMN, -c COLUMN
                        the column from which to read domain names in the CSV
                        input (default: 'Domain Name')
  --size SIZE, -s SIZE  the viewport size, in the form 'WxH' (default:
                        '1024x768')
  --dir OUTDIR, -d OUTDIR
                        the directory into which screenshots should be written
  --output OUTPUT, -o OUTPUT
                        the filename of the CSV output
  --full, -F            capture the full page height (default: only capture
                        the viewport)
  --thumb THUMB, -t THUMB
                        the max thumbnail width, in pixels
  --wait, -w            wait for the document to be fully loaded (?) before
                        taking a screenshot
  --ttl TTL             the screenshot time to live, in seconds
```

The [Makefile](https://github.com/shawnbot/dotgov-screenshots/blob/master/Makefile) uses `capture.py` to parse the CSV of .gov domain names like so:

```sh
python capture.py
		--full \                    # capture full-page images
		--dir screenshots \         # output PNGs to screenshots/
		--column "Domain Name" \    # get domain names from the "Domain Name" column
		-o screenshots/status.csv \ # output CSV to screenshots/status.csv
		domains.csv                 # load data from domains.csv
```
