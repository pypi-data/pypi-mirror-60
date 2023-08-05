import logging

from .api_client import RlecClient

# TODO: Most of the tests require an actual cluster and are stateful...

logger = logging.getLogger(__name__)


def test_init_client():
    client = RlecClient()


bdb_creation_payload = {  # TODO: move this out
    'name': 'test-bdb-1',
    'memory_size': 1 * 1024 ** 2,
    'shards_count': 1,
    'replication': True,
    'shards_placement': 'sparse',
    'proxy_policy': 'all-master-shards',
    'oss_cluster': True,
    'shard_key_regex': [{'regex': '.*\{(?<tag>.*)\}.*'}, {'regex': '(?<tag>.*)'}],
    'sharding': True,
    'data_persistence': 'snapshot',  # 'aof' for AOF (defaults to AOF every sec)
    'snapshot_policy': [{'secs': 1, 'writes': 1}],
    'tls_mode': 'enabled',
    'enforce_client_authentication': 'disabled'
}


def test_get_cluster():
    client = RlecClient()
    cluster = client.get_cluster()


def test_bdb_flow():
    client = RlecClient()

    response = client.create_bdb(bdb_creation_payload)
    new_bdb_uid = response['uid']
    logger.info('New bdb created: %s...', new_bdb_uid)
    client.wait_for_action(response['action_uid'])

    logger.info('Updating bdb %s...', new_bdb_uid)
    res = client.update_bdb(new_bdb_uid, {'memory_size': 2 * 1024 ** 2})
    client.wait_for_action(res['action_uid'])

    logger.info('Deleting bdb %s...', new_bdb_uid)
    response = client.delete_bdb(new_bdb_uid)
    client.wait_for_action(response['action_uid'])


def test_turn_maintenance_mode_on_off():
    client = RlecClient()

    node_uid = 1
    logger.info('Node {}: turning maintenance mode ON'.format(node_uid))
    response = client.perform_node_action(node_uid, action_name='maintenance_on')
    client.wait_for_action(response['task_id'])

    logger.info('Node {}: turning maintenance mode OFF'.format(node_uid))
    response = client.perform_node_action(node_uid, action_name='maintenance_off')
    client.wait_for_action(response['task_id'])
