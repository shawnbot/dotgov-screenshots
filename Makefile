all: screenshots

screenshots: domains.csv
	mkdir -p $@
	time python capture.py \
		--outdir $@ --column "Domain Name" \
		-o $@/status.csv $<

domains.csv:
	curl -s "https://gsa.github.io/data/dotgov-domains/2014-12-01-full.csv" > $@

clean:
	rm -rf screenshots

distclean:
	rm -f domains.csv
