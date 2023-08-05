import json
import os
from contextlib import closing
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from .methods import APIMethod, MethodTableCache
from .utils import TypeChecker, encode_multipart_formdata

missing = object()


class Etsy:
    api_version = "v2"

    def __init__(
        self,
        oauth_env,
        api_key="",
        etsy_oauth_client=None,
        method_cache=missing,
        log=None,
    ):
        """
        Creates a new API instance. When called with no arguments,
        reads the appropriate API key from the default ($HOME/.etsy/keys)
        file.

        Parameters:
            api_key      - An explicit API key to use.
            method_cache - A file to save the API method table in for
                           24 hours. This speeds up the creation of API
                           objects.
            log          - An callable that accepts a string parameter.
                           Receives log messages. No logging is done if
                           this is None.

        If method_cache is explicitly set to None, no method table
        caching is performed. If the parameter is not passed, a file in
        $HOME/.etsy is used if that directory exists. Otherwise, a
        temp file is used.
        """
        self.api_key = api_key
        self.etsy_oauth_client = etsy_oauth_client
        self.log = log or self._ignore

        self.api_url = oauth_env.api_url
        if self.api_url.endswith("/"):
            raise AssertionError("api_url should not end with a slash.")

        if not callable(self.log):
            raise ValueError("log must be a callable.")

        self.type_checker = TypeChecker()

        self.log(
            "Creating %s Etsy API, base url=%s." % (self.api_version, self.api_url)
        )
        self._get_methods(method_cache)

    def _ignore(self, _):
        pass

    def _get_methods(self, method_cache):
        self.method_cache = MethodTableCache(self, method_cache, missing=missing)
        is_success, message, objects = self.method_cache.get()
        try:
            ms = objects["results"]["results"]
        except (KeyError, TypeError):
            raise Exception("Нет доступа к API Etsy.")

        self._methods = dict([(m["name"], m) for m in ms])

        for method in ms:
            setattr(self, method["name"], APIMethod(self, method))

    def etsy_home(self):
        return os.path.expanduser("~/.etsy")

    def get_method_table(self):
        return self._get("GET", "/")

    def _get_url(self, url, http_method, content_type, body):
        if self.etsy_oauth_client is not None:
            response, data = self.etsy_oauth_client.do_oauth_request(
                url, http_method, content_type, body
            )
            is_success = bool(str(response.get("status", "")).startswith("2"))
        else:
            response = None
            try:
                with closing(urlopen(url)) as f:
                    data = f.read()
            except HTTPError as err:
                is_success = False
                data = err
            else:
                is_success = True
        return is_success, data, response

    def _get(self, http_method, url, **kwargs):
        if self.api_key:
            kwargs.update(dict(api_key=self.api_key))

        if http_method == "POST":
            url = f"{self.api_url}{url}"
            fields = []
            files = []

            for name, value in kwargs.items():
                if hasattr(value, "read"):
                    files.append((name, value.name, value.read()))
                else:
                    fields.append((name, str(value)))

            content_type, body = encode_multipart_formdata(fields, files)
        else:
            url = f"{self.api_url}{url}?{urlencode(kwargs)}"
            body = b""
            content_type = None

        is_success, data, response = self._get_url(url, http_method, content_type, body)

        objects = {"response": response}

        try:
            data = data.decode()
        except (UnicodeDecodeError, AttributeError):
            pass

        if is_success:
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise ValueError(f"Could not decode response from Etsy as JSON: {data}")
            else:
                message = ""
                objects.update({"results": data})
        else:
            message = data
            objects.update({"data": data})

        return is_success, message, objects
