# .gov screenshots
This little app grabs screenshots of
[.gov domains](https://18f.gsa.gov/2014/12/18/a-complete-list-of-gov-domains/)
using [PhantomJS](http://phantomjs.org/). To run it, clone the repository and
run the following:

```sh
$ npm install       # install dependencies
$ npm run capture   # take some screenshots
```

This will take some time. A delay is built into screenshot to account for
layout adjustments made in JavaScript (though we don't wait for all images to
load) and, though several screenshots are taken in parallel at any given
moment, most sites will take 2-3 seconds to load (depending on your own
internet connection).
