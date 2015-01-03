#!/usr/bin/env node
"use strict";


// imports
var fs = require("fs"),
    path = require("path"),
    async = require("async"),
    csv = require("fast-csv"),
    spawn = require("child_process").spawn;

var COLORS = 5,
    CSV_FILENAME = "domains.csv",
    COMMAND = "convert",
    ARGS = ["-resize", "600x600>", "-colors", COLORS, "-unique-colors", "-scale", "1000%"],
    SUFFIX = "-palette";

var reader = csv.parse({headers: true}),
    input = fs.createReadStream(CSV_FILENAME)
      .pipe(reader)
      .on("data", add)
      .on("end", end),
    tasks = [],
    errors = 0;

function add(row) {
  row.palette = row.image.replace(/(\.png)$/, SUFFIX + "$1");
  tasks.push(row);
}

function end() {
  async.mapLimit(tasks, 3, function(task, next) {
    var args = ARGS.concat([task.image, task.palette]),
        convert = spawn(COMMAND, args);
    convert.stderr.pipe(process.stderr);
    convert.on("close", function(code) {
      convert.stderr.unpipe(process.stderr);
      if (code !== 0) {
        console.error("(x) error generating palette from %s", task.image);
        errors++;
        return next(null, task);
      }
      console.log("(✓) done: %s -> %s", task.image, task.palette);
      next(null, task);
    });
  }, function(error, results) {
    console.log("... processed %d images with %d errors", results.length, errors);
  });
}
