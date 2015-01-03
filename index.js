#!/usr/bin/env node
"use strict";

// imports
var fs = require("fs"),
    path = require("path"),
    async = require("async"),
    request = require("request"),
    csv = require("fast-csv"),
    screenshot = require("screenshot-stream");

// inputs
var CSV_URL = "https://gsa.github.io/data/dotgov-domains/2014-12-01-full.csv",
    DOMAIN_COLUMN = "Domain Name",
    SIZE = "1280x960",
    OPTIONS = {delay: .01},
    OUTDIR = "screenshots",
    MAX_PARALLEL = 5;

// CSV reader, writer, and Pageres instance
var reader = csv.parse({
      headers: true
    }),
    input = request(CSV_URL)
      .pipe(reader)
      .on("data", add)
      .on("end", end),
    output = fs.createWriteStream("domains.csv"),
    writer = csv.createWriteStream({
        headers: true
      }),
    tasks = [],
    errors = 0;

writer.pipe(output);

/*
 * XXX remove me
 */
function filter(row) {
  return row["Domain Type"] === "Federal Agency";
}

function add(row) {
  var domain = row[DOMAIN_COLUMN].toLowerCase(),
      image = path.join(OUTDIR, domain) + ".png";
  row.url = "http://" + domain;
  row.domain = domain; // normalized
  row.image = image;
  if (filter(row)) {
    tasks.push(row);
  }
}

function end() {
  console.log("capturing %d domains...", tasks.length);
  async.mapLimit(tasks, MAX_PARALLEL, function(task, next) {
    var written = false;
    if (fs.existsSync(task.image) && fs.statSync(task.image).size > 0) {
      written = true;
      return done();
    }

    var image = fs.createWriteStream(task.image),
        shot = screenshot(task.url, SIZE, OPTIONS)
          .on("warn", function(warning) {
            // console.warn("warning:", warning);
          })
          .on("error", function(error) {
            console.error("(x) error with %s: '%s'", task.domain, error);
            task.error = error;
            errors++;
            next(null, task);
          })
          .on("data", function() {
            written = true;
          })
          .on("end", done)
          .on("close", done)
          .pipe(image);

    function done() {
      if (!written) {
        fs.unlink(task.image, function() {
          console.log("(x) no image saved for %s (unlinked %s)", task.domain, task.image);
          task.error = "no image written";
          return next(null, task);
        });
      }
      console.log("(✓) done: %s", task.domain);
      writer.write(task);
      next(null, task);
    }
  }, function(error, results) {
    console.log("... processed %d tasks with %d errors", results.length, errors);
  });
}
