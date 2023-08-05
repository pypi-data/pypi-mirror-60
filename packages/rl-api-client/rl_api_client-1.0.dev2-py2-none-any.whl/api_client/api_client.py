import logging
import time
from requests.exceptions import ConnectionError, HTTPError, Timeout

from typing import Optional

from . import http_client
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CNM_HTTP_PORT = 8080
CNM_HTTPS_PORT = 9443
RLEC_API_VERSION = 'v1'
DEFAULT_HOST = '127.0.0.1'
DEFAULT_USERNAME = 'demo@redislabs.com'
DEFAULT_PASSWORD = '123456'
DEFAULT_PROTOCOL = 'https'


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# TODO: Can we do this in Python3?
# TODO: Create an even higher-level client similar to RCP client? With waiters/futures and other utility functions?


class RlecClient(object):
    def __init__(self, host=DEFAULT_HOST, user=DEFAULT_USERNAME, password=DEFAULT_PASSWORD, port=CNM_HTTPS_PORT,
                 protocol=DEFAULT_PROTOCOL, api_version=RLEC_API_VERSION):
        # type (str, str, str, int, str) -> None
        self.client = http_client.HttpClient(
            host, user, password, port=port, protocol=protocol, api_version=api_version
        )

    def verify_connection(self):
        # type: () -> None
        """
        Raise an Exception if the client cannot establish a connection with the provided cluster.
        """
        self.get_bootstrap()

    def wait_for_connection(self, timeout=30):
        # type: (Optional[int]) -> None
        """
        Wait until connection with the cluster establishes, up to `timeout` seconds
        """
        url = self.client.base_url

        start_time = time.time()
        while time.time() < start_time + timeout:
            try:
                self.verify_connection()
                logger.info('Successfully connected to {}!'.format(url))
                return
            except (ConnectionError, HTTPError, Timeout) as connection_error:
                logger.debug('Connection failed: {}. Retrying...'.format(connection_error))
                time.sleep(1)
        raise RuntimeError('Could not connect to {} after {} seconds'.format(url, timeout))

    def get_action(self, action_uid):
        # type: (str) -> dict
        res = self.client.get('actions/{}'.format(action_uid))
        return res.json()

    def wait_for_action(self, action_uid):
        # type: (str) -> None
        """
        Block until an action with the given uid is completed. Raise an error if the action fails or cannot be found.
        """
        while True:
            action = self.get_action(action_uid)
            # TODO: Handle `action not found` error
            status = action['status']
            if status in ['running', 'pending']:
                time.sleep(0.3)
            elif status == 'error':
                raise Exception('Error during action! {}'.format(action))
            elif status == 'completed':
                logger.info('Done with action {}: {}'.format(action_uid, action))
                break

    def get_bootstrap(self):
        # type: () -> dict
        return self.client.get('bootstrap')

    def get_bdb(self, bdb_uid):
        # type: (int) -> dict
        res = self.client.get('bdbs/{}'.format(bdb_uid))
        return res.json()

    def get_all_bdbs(self):
        # type: () -> list[dict]
        res = self.client.get('bdbs')
        return res.json()

    def create_bdb(self, payload):
        # type: (dict) -> dict
        res = self.client.post('bdbs', json=payload)
        return res.json()

    def update_bdb(self, uid, payload):
        # type: (int, dict) -> dict
        res = self.client.put('bdbs/{}'.format(uid), json=payload)
        return res.json()

    def delete_bdb(self, uid):
        # type: (int) -> dict
        # TODO: bdb_uid is int or str?
        res = self.client.delete('bdbs/{}'.format(uid))
        return res.json()

    def get_all_actions(self):
        # type: () -> dict
        return self.client.get('actions').json()

    def update_cluster(self, payload):
        # type: (dict) -> dict
        return self.client.put('cluster', json=payload).json()

    def get_cluster(self):
        # type: () -> dict
        return self.client.get('cluster').json()

    # TODO: some APIs like this one don't require authentication, yet the client does
    # TODO: Add `join_cluster`
    def create_cluster(self, request_body):
        # type: (dict) -> dict
        # body = {
        #     'action': 'create_cluster',
        #     'cluster': {
        #         'nodes': [],
        #         'name': name
        #     },
        #     'credentials': {
        #         'username': admin_user,
        #         'password': admin_password
        #     }
        # }
        return self.client.post('bootstrap/create_cluster', json=request_body)

    def export_bdb(self, bdb_uid, data):
        # type: (int, dict) -> None
        # TODO add & handle action_uid
        self._perform_bdb_action(bdb_uid, 'export', data)

    def _perform_bdb_action(self, bdb_uid, action_name, data):
        # type: (int, str, dict) -> None
        # TODO add & handle action_uid
        url = 'bdbs/{}/actions/{}'.format(bdb_uid, action_name)
        response = self.client.post(url, json=data)
        assert response.ok

    def perform_node_action(self, node_uid, action_name):
        # type: (int, str) -> dict
        # TODO: private?
        url = 'nodes/{}/actions/{}'.format(node_uid, action_name)
        return self.client.post(url, json={}).json()
