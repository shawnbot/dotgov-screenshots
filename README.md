# .gov screenshots

This repo grabs [.gov domains](https://catalog.data.gov/dataset/gov-domains-api) and
generates screenshots of each site using [webkit2png](http://www.paulhammond.org/webkit2png/).

Make sure you have GNU Make and Python, then run `make` in this directory to generate
the screenshots directory. On average, each domain takes about 5 seconds to screenshot,
so you're looking at about an hour and 15 minutes to get them all.

Afterward, pop open `index.html` to view the screenshots. You'll need to do this in Apache
or using another webserver (e.g. `python -m SimpleHTTPServer`) because browsers disable XHR
requests from `file:///` URLs.
