"""


Agent Services


"""

from urllib.parse import urlparse, urljoin


SERVICES = {
    'metadata': {
        'type': 'Ocean.Meta.{VERSION}',
        'url': '{BASE_URL}/api/{VERSION}/meta/data',
    },
    'storage': {
        'type': 'Ocean.Storage.{VERSION}',
        'url': '{BASE_URL}/api/{VERSION}/assets',
    },
    'invoke': {
        'type': 'Ocean.Invoke.{VERSION}',
        'url': '{BASE_URL}/api/{VERSION}/invoke',
    },
    'market': {
        'type': 'Ocean.Market.{VERSION}',
        'url': '{BASE_URL}/api/{VERSION}/market',
    },
    'trust': {
        'type': 'Ocean.Trust.{VERSION}',
        'url': '{BASE_URL}/api/{VERSION}/trust',
    },
    'auth': {
        'type': 'Ocean.Auth.{VERSION}',
        'url': '{BASE_URL}/api/{VERSION}/auth',
    },
}

ALL_SERVICES=SERVICES.keys()

class Services:


    def __init__(self, base_url=None, service_list=None, version=None):
        self._base_url = base_url
        self._version = version
        if version is None:
            self._version = 'v1'
        self._items = {}
        if service_list:
            if self._base_url is None:
                raise ValueError('you must provide a base URL')
            for service_name in service_list:
                self.add(service_name)

    def add(self, name, url_or_uri=None, service_type=None, version=None):
        if url_or_uri is None and self._base_url is None:
            raise ValueError('you must provide a base URL or service URL')

        if name not in SERVICES:
            raise ValueError(f'service name {name} is not a valid service name')

        url = self._get_url(name, url_or_uri, version)
        service_type = self._get_service_type(name, service_type, version)
        self._items[name] = {
            'type': service_type,
            'url': url
        }

    def _get_url(self, name, url_or_uri=None, version=None):
        if version is None:
            version = self._version
        if url_or_uri is None:
            url_or_uri = SERVICES[name]['url'].format(BASE_URL=self._base_url, VERSION = version)
        url = url_or_uri
        info = urlparse(url)
        if not info.scheme:
            url = urljoin(self._base_url, url)
        return url

    def _get_service_type(self, name, service_type=None, version=None):
        if version is None:
            version = self._version
        if service_type is None:
            service_type = SERVICES[name]['type'].format(VERSION = version)

        return service_type

    @property
    def as_dict(self):
        return self._items

    @property
    def names(self):
        return self._items.keys()
