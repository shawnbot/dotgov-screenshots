#!/usr/bin/env node
"use strict";

// imports
var fs = require("fs"),
    path = require("path"),
    async = require("async"),
    request = require("request"),
    csv = require("fast-csv"),
    screenshot = require("screenshot-stream"),
    colors = require("colors");

// inputs
var CSV_URL = "https://gsa.github.io/data/dotgov-domains/2014-12-01-full.csv",
    DOMAIN_COLUMN = "Domain Name",
    SIZE = "1280x600",
    OPTIONS = {delay: .1},
    OUTDIR = "screenshots",
    MAX_PARALLEL = 5;

// CSV reader, writer, and Pageres instance
var reader = csv.parse({headers: true}),
    input = request(CSV_URL)
      .pipe(reader)
      .on("data", queue)
      .on("end", end),
    output = fs.createWriteStream("domains.csv"),
    writer = csv.createWriteStream({headers: true}),
    tasks = [],
    errors = 0;

writer.pipe(output);

/*
 * XXX remove me
 */
function filter(row) {
  return row["Domain Type"] === "Federal Agency";
}

function queue(row) {
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
  // tasks = tasks.slice(0, 25);

  console.log("capturing %d domains...", tasks.length);
  // sort tasks by domain ascending
  tasks.sort(function(a, b) {
    return ascending(a.domain, b.domain);
  });

  async.mapLimit(tasks, MAX_PARALLEL, function(task, next) {

    if (fs.existsSync(task.image) && fs.statSync(task.image).size > 0) {
      console.log("• %s skipped: %s already exists".yellow, task.domain, task.image);
      writer.write(task);
      return next(null, task);
    }

    // console.log("( ) capturing %s ...", task.domain);

    var image = fs.createWriteStream(task.image),
        written = false,
        alreadyDone = false,
        time = Date.now(),
        shot = screenshot(task.url, SIZE, OPTIONS)
          .on("warn", function(warning) {
            // console.warn("warning:", warning);
          })
          .once("error", function(error) {
            task.error = ellipses(error, 24);
            done();
          })
          .once("data", function() {
            written = true;
          })
          .on("end", done)
          .pipe(image);

    function done() {
      if (alreadyDone) {
        return console.error("✗✗✗ already done: %s".red, task.domain);
      }
      task.duration = (Date.now() - time) / 1000;
      alreadyDone = true;
      image.end();
      if (task.error || !written) {
        if (task.error) {
          console.warn("✗ %s error: '%s'".red, task.domain, ellipses(task.error, 32));
        } else {
          console.warn("✗ %s error: no image, unlinking %s.red", task.domain, task.image);
        }
        errors++;
        return fs.unlink(task.image, function() {
          return next(null, task);
        });
      }
      console.log("✓ %s → %s in %ss".green, task.domain, task.image, task.duration.toFixed(2).white);
      writer.write(task);
      next(null, task);
    }
  }, function(error, results) {
    console.log("processed %d tasks with %d errors", results.length, errors);
    cleanup();
  });
}

function cleanup() {
  output.close();
}

function ascending(a, b) {
  return a > b ? 1 : a < b ? -1 : 0;
}

function ellipses(str, maxLength) {
  return str.length > maxLength
    ? str.slice(0, maxLength) + "..."
    : str;
}
