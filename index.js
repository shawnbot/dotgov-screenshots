#!/usr/bin/env node
"use strict";

// imports
var fs = require("fs"),
    path = require("path"),
    request = require("request"),
    csv = require("fast-csv"),
    Pageres = require("pageres");

// inputs
var CSV_URL = "https://gsa.github.io/data/dotgov-domains/2014-12-01-full.csv",
    DOMAIN_COLUMN = "Domain Name",
    SIZES = ["1280x960"],
    OUTDIR = "screenshots";

// CSV reader, writer, and Pageres instance
var reader = csv.parse({
      headers: true
    }),
    writer = csv.createWriteStream({
      headers: true
    }),
    pager = new Pageres({
        delay: .01,
        filename: "<%= url %>"
      })
      .dest(".")
      .on("warn", warn),
    output = fs.createWriteStream("domains.csv"),
    capturing = 0;

writer.pipe(output);

request(CSV_URL)
  .pipe(reader)
  .on("data", add)
  .on("end", end);

function warn(warning) {
  console.warn("*", warning);
}

function add(row) {
  var domain = row[DOMAIN_COLUMN].toLowerCase(),
      filename = path.join(OUTDIR, domain);
  row.domain = domain; // normalized
  row.image = filename; // relative path to the image
  writer.write(row);

  pager.src(domain, SIZES, {filename: filename});
  capturing++;
}

function end() {
  writer.end();
  console.log("capturing %d rows...", capturing);
  pager.run(function(error) {
    if (error) return console.error("error:", error);
    console.log("done!");
  });
}
