all: screenshots

screenshots: domains.csv
	mkdir -p $@
	time python render.py $< $@

domains.csv:
	curl -s "https://gsa.github.io/data/dotgov-domains/2014-12-01-full.csv" > $@

clean:
	rm -rf screenshots

distclean:
	rm -f domains.csv
