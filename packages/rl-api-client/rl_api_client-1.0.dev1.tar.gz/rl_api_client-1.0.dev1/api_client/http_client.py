"""
This file provides a convenient method of communicating with HTTP APIs.
"""
import json
import logging

import requests
from requests.auth import HTTPBasicAuth
from urlparse import urlparse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DEFAULT_API_VERSION = 'v1'


class HttpClient(object):
    """
    Convenience class for connecting to an HTTP API.
    """
    def __init__(self, host, username, password, port, protocol='https', api_version=DEFAULT_API_VERSION,
                 auth_class=HTTPBasicAuth, verify=False, allow_redirects=True):
        self._host = host
        self._port = port
        self._protocol = protocol
        self._api_version = api_version
        self._verify = verify
        self._username = username
        self._password = password
        self._auth_class = auth_class
        self._allow_redirects = allow_redirects

    @property
    def base_url(self):
        # type: () -> str
        """
        :return: Base url, for example: http://www.redislabs.com:8443/v1/
        """
        return '{protocol}://{host}:{port}/{api_version}/'.format(
            protocol=self._protocol, host=self._host, port=self._port, api_version=self._api_version
        )

    def _request(self, method, path, **kwargs):
        url = self.base_url + path
        if 'auth' not in kwargs:
            kwargs['auth'] = self._auth_class(self._username, self._password)

        if 'json' in kwargs:
            kwargs['data'] = json.dumps(kwargs['json'])
            kwargs['headers'] = {'Content-Type': 'application/json'}

        if isinstance(url, bytes):
            url = url.decode()

        allow_redirects = kwargs.get('allow_redirects', self._allow_redirects)
        verify = kwargs.get('verify', self._verify)

        try:
            # TODO: verify
            response = requests.request(method, url, verify=verify, allow_redirects=allow_redirects, **kwargs)
        except (requests.ConnectionError, requests.ConnectTimeout) as e:
            raise Exception(str(e))

        if not response.ok:
            logger.warning(
                'Request failed: [{method}], [{url}], '
                'details: {details}'
                .format(
                    method=method, url=url, details=response.text)
                )
            response.raise_for_status()

        # Standard redirection will not forward the auth header, see: https://github.com/psf/requests/issues/2949
        if response.is_redirect:
            new_url = response.headers['location']
            self._host = urlparse(new_url).netloc.split(':')[0]
            response = self._request(method, path, verify=verify, **kwargs)
        return response

    def post(self, url, **kwargs):
        return self._request('post', url, **kwargs)

    def get(self, url, **kwargs):
        return self._request('get', url, **kwargs)

    def put(self, url, **kwargs):
        return self._request('put', url, **kwargs)

    def delete(self, url, **kwargs):
        return self._request('delete', url, **kwargs)

# TODO
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
