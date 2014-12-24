import urllib, hashlib, json

OK = "ok"
ERROR = "error"

class API(object):
    def __init__(self, key, secret, version=6):
        """
        Create a new API wrapper object with the (required) API key
        and secret (strings beginning with "P" and "S",
        respectively). You can find yours here:

        https://www.url2png.com/dashboard/
        """
        self.api_key = key
        self.api_secret = secret
        self.api_version = version

    def get_token(self, query):
        """
        Get the request token for a given query string, which is MD5
        hashed with the API secret provided in the constructor.
        """
        return hashlib.md5(query + self.api_secret).hexdigest()

    def get_query(self, url, params=None):
        """
        Get the query string for a given screenshot URL and optional
        parameters dict.
        """
        query = {'url': url}
        if params:
            query.update(params)
        return "?" + urllib.urlencode(query)

    def get_url(self, url, params=None, fmt="json"):
        """
        Get the url2png API URL for a given screenshot URL, optional
        request parameters, and response format ("png" or "json",
        the default).
        """
        query = self.get_query(url, params)
        return "http://api.url2png.com/v%d/%s/%s/%s/%s" % (
            self.api_version,
            self.api_key,
            self.get_token(query),
            fmt, query
        )

    def get_json(self, url, params=None, max_tries=0):
        """
        Capture a screenshot and return the JSON API response. You
        can test the success of the capture with:

        response["status"] == url2png.OK
        """
        json_url = self.get_url(url, params, fmt="json")
        req = urllib.urlopen(json_url)
        try:
            return json.load(req)
        except:
            return False

    def capture(self, url, params=None, **kwargs):
        """
        This is essentially an alias to get_json()
        """
        return self.get_json(url, **kwargs)

    def make_params(self, args):
        """
        Built parameters from either a dict or object of arguments
        (e.g. parsed by argparse.ArgumentParser). This looks for
        dict keys (or object attrs) named:

        - "size" or "viewport" (viewport dimensions, "WxH")
        - "full" or "fullpage" (boolean -> "true" | "false")
        - "thumb" or "thumbnail_max_width" (an integer)
        - "unique" (a unique value to force new captures)
        - "wait" or "say_cheese" (if present, always "true")
        - "ttl" (time to live, in seconds)

        and returns a dict with the named paramters suitable for
        passing to get_query(), get_url() or get_json()
        """
        if type(args) is dict:
            has = args.has_key
            get = args.get
        else:
            has = lambda k: hasattr(args, k) and getattr(args, k) is not None
            get = lambda k: getattr(args, k)
        trans = (
            ("size", "viewport", str),
            ("full", "fullpage", lambda b: str(b).lower()),
            ("thumb", "thumbnail_max_width", str),
            ("unique", "unique", str),
            ("wait", "say_cheese", lambda x: "true"),
            ("ttl", "ttl", str)
        )
        params = {}
        for src, dest, read in trans:
            if has(src):
                params[dest] = read(get(src))
            elif has(dest):
                params[dest] = read(get(dest))
        return params
