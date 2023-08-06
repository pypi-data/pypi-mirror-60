import json
from abc import abstractmethod
from contextlib import closing
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from .methods import APIMethod, MethodTableCache
from .utils import TypeChecker, encode_multipart_formdata

missing = object()


class EtsyAPI:
    api_version = "v2"

    def __init__(
        self, oauth_env, api_key="", oauth_client=None, method_cache=missing,
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

        If method_cache is explicitly set to None, no method table
        caching is performed. If the parameter is not passed, a file in
        $HOME/.etsy is used if that directory exists. Otherwise, a
        temp file is used.
        """
        self.api_key = api_key
        self.oauth_client = oauth_client
        self.type_checker = TypeChecker()

        self.log = lambda x: None

        self.api_url = oauth_env.api_url
        if self.api_url.endswith("/"):
            raise AssertionError("api_url should not end with a slash.")

        self.set_available_methods(method_cache)

    def get_method_table(self):
        return self._get("GET", "/")

    def set_available_methods(self, method_cache):
        self.method_cache = MethodTableCache(self, method_cache, missing=missing)
        is_success, message, objects = self.method_cache.get()
        if not is_success:
            raise Exception(f"Нет доступа к API Etsy.\n{message}")

        method_list = objects["results"]
        assert isinstance(method_list, list), ""

        self.available_methods = {
            method["name"]: APIMethod(self, method) for method in method_list
        }

    def _get_url(self, url, http_method, content_type, body):
        if self.oauth_client is not None:
            response, data = self.oauth_client.do_oauth_request(
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

        objects = {
            "response": {
                key: value
                for key, value in response.items()
                if key
                in ["x-ratelimit-limit", "x-ratelimit-remaining", "date", "status",]
            }
        }

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
                if isinstance(data, dict):
                    objects.update(data)
                else:
                    objects.update({"results": data})
        else:
            message = data
            objects.update({"data": data})

        return is_success, message, objects

    @abstractmethod
    def api_method_name(self):
        pass

    def make_request(self, **params):
        try:
            api_method = self.available_methods[self.api_method_name]
        except KeyError:
            raise AttributeError(f'Метод "{self.api_method_name}" не определён.')

        return api_method(**params)
