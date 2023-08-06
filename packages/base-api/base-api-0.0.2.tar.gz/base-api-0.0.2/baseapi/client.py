from importlib import import_module

from .apis import Api
from .exceptions import ClientException


class Client:
    DEFAULT_URL = None
    DEFAULT_APIS = ()

    def __init__(self, url=None, jwt=None):
        self.url = url or self.DEFAULT_URL
        self.jwt = jwt
        self.apis = []
        self.load_apis()

    def load_apis(self):
        for api_name in self.DEFAULT_APIS:
            module = import_module(api_name)
            for cls in module.__dict__.values():
                if self.is_valid_api(cls):
                    self.add_api(cls(self))

    def is_valid_api(self, cls):
        try:
            return issubclass(cls, Api) and cls != Api
        except TypeError:
            return False

    def add_api(self, api):
        self.apis.append(api)
        for attr_name in dir(api):
            attr = getattr(api, attr_name)
            if getattr(attr, 'expose', False):
                self.expose_api_method(attr_name, attr)

    def expose_api_method(self, name, method):
        if getattr(self, name, None) is not None:
            raise ClientException(f'Name already exists on client: {name}')
        setattr(self, name, method)
