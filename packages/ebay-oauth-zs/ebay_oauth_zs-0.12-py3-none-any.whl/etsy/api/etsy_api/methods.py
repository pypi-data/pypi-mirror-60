import json
import os
import re
import tempfile
import time

# from .utils import TypeChecker


class APIMethod:
    def __init__(self, api, spec):
        """
        Parameters:
            api          - API object that this method is associated with.
            spec         - dict with the method specification; e.g.:

              {'name': 'createListing', 'uri': '/listings', 'visibility':
              'private', 'http_method': 'POST', 'params': {'description':
              'text', 'tags': 'array(string)', 'price': 'float', 'title':
              'string', 'materials': 'array(string)', 'shipping_template_id':
              'int', 'quantity': 'int', 'shop_section_id': 'int'}, 'defaults':
              {'materials': None, 'shop_section_id': None}, 'type': 'Listing',
              'description': 'Creates a new Listing'}
        """

        self.api = api
        self.spec = spec
        self.type_checker = self.api.type_checker
        # self.type_checker = TypeChecker()
        self.__doc__ = self.spec["description"]
        self.compiled = False

    def __call__(self, *args, **kwargs):
        if not self.compiled:
            self.compile()
        return self.invoke(*args, **kwargs)

    def compile(self):
        uri = self.spec["uri"]
        self.positionals = re.findall("{(.*)}", uri)

        for p in self.positionals:
            uri = uri.replace("{%s}" % p, "%%(%s)s" % p)
        self.uri_format = uri

        self.compiled = True

    def invoke(self, *args, **kwargs):
        if args and not self.positionals:
            raise ValueError(
                "Positional argument(s): %s provided, but this method does "
                "not support them." % (args,)
            )

        if len(args) > len(self.positionals):
            raise ValueError("Too many positional arguments.")

        for k, v in zip(self.positionals, args):
            if k in kwargs:
                raise ValueError("Positional argument duplicated in kwargs: %s" % k)
            kwargs[k] = v

        ps = {}
        for p in self.positionals:
            if p not in kwargs:
                raise ValueError("Required argument '%s' not provided." % p)
            ps[p] = kwargs[p]
            del kwargs[p]

        self.type_checker(self.spec, **kwargs)
        return self.api._get(self.spec["http_method"], self.uri_format % ps, **kwargs)


class MethodTableCache:
    max_age = 60 * 60 * 24

    def __init__(self, api, method_cache, missing):
        self.api = api
        self.filename = self.resolve_file(method_cache, missing)
        self.used_cache = False
        self.wrote_cache = False

    def resolve_file(self, method_cache, missing):
        if method_cache is missing:
            return self.default_file()
        return method_cache

    def etsy_home(self):
        return os.path.expanduser("~/.etsy")

    def default_file(self):
        etsy_home = self.etsy_home()
        d = etsy_home if os.path.isdir(etsy_home) else tempfile.gettempdir()
        return os.path.join(d, f"methods.{self.api.api_version}.json")

    def get(self):
        ms = self.get_cached()
        if not ms:
            ms = self.api.get_method_table()
            self.cache(ms)
        return ms

    def get_cached(self):
        if self.filename is None or not os.path.isfile(self.filename):
            self.api.log("Not using cached method table.")
            return None
        if time.time() - os.stat(self.filename).st_mtime > self.max_age:
            self.api.log("Method table too old.")
            return None
        with open(self.filename, "r") as f:
            self.used_cache = True
            self.api.log("Reading method table cache: %s" % self.filename)
            try:
                return json.loads(f.read())
            except json.JSONDecodeError:
                raise Exception("Нет доступа к API Etsy.")

    def cache(self, methods):
        if self.filename is None:
            self.api.log("Method table caching disabled, not writing new cache.")
            return
        with open(self.filename, "w") as f:
            json.dump(methods, f)
            self.wrote_cache = True
            self.api.log("Wrote method table cache: %s" % self.filename)
