outdir ?= screenshots
domains_csv_url ?= https://gsa.github.io/data/dotgov-domains/2014-12-01-full.csv

all: capture

capture: domains.csv
	mkdir -p $(outdir)
	time python capture.py \
		--outdir $(outdir) --column "Domain Name" \
		-o $(outdir)/status.csv $<

domains.csv:
	curl -s "$(domains_csv_url)" > $@

domains-federal.csv:
	(curl -s "$(domains_csv_url)" | csvfilter --filter "get('Domain Type').startswith('Federal')") > $@

clean:
	rm -rf $(outdir)

distclean:
	rm -f domains.csv
