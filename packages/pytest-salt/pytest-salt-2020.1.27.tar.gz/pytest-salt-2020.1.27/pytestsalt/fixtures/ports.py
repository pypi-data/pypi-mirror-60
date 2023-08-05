# -*- coding: utf-8 -*-
'''
pytestsalt.fixtures.ports
~~~~~~~~~~~~~~~~~~~~~~~~~

Pytest salt plugin ports fixtures
'''

# Import python libs
from __future__ import absolute_import

# Import 3rd-party libs
import pytest

# Import pytestsalt libs
from pytestsalt.utils import get_unused_localhost_port


@pytest.fixture
def master_publish_port():
    '''
    Returns an unused localhost port for the master publish interface
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_publish_port():
    '''
    Returns an unused localhost port for the master publish interface
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_return_port():
    '''
    Returns an unused localhost port for the master return interface
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_return_port():
    '''
    Returns an unused localhost port for the master return interface
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_tcp_master_pub_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_tcp_master_pub_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_tcp_master_pull_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_tcp_master_pull_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_tcp_master_publish_pull():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_tcp_master_publish_pull():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_tcp_master_workers():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_tcp_master_workers():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_engine_port():
    '''
    Returns an unused localhost port for the pytest salt master engine
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_engine_port():
    '''
    Returns an unused localhost port for the pytest session salt master engine
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_of_masters_publish_port():
    '''
    Returns an unused localhost port for the master publish interface
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_of_masters_publish_port():
    '''
    Returns an unused localhost port for the master publish interface
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_of_masters_return_port():
    '''
    Returns an unused localhost port for the master return interface
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_of_masters_return_port():
    '''
    Returns an unused localhost port for the master return interface
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_of_masters_master_tcp_master_pub_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_of_masters_master_tcp_master_pub_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_of_masters_master_tcp_master_pull_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_of_masters_master_tcp_master_pull_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_of_masters_master_tcp_master_publish_pull():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_of_masters_master_tcp_master_publish_pull():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_of_masters_master_tcp_master_workers():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_of_masters_master_tcp_master_workers():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def master_of_masters_engine_port():
    '''
    Returns an unused localhost port for the pytest salt master engine
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_master_of_masters_engine_port():
    '''
    Returns an unused localhost port for the pytest session salt master engine
    '''
    return get_unused_localhost_port()


@pytest.fixture
def minion_tcp_pub_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_minion_tcp_pub_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def minion_tcp_pull_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_minion_tcp_pull_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def proxy_tcp_pub_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_proxy_tcp_pub_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def proxy_tcp_pull_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_proxy_tcp_pull_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def minion_engine_port():
    '''
    Returns an unused localhost port for the pytest salt minion engine
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_minion_engine_port():
    '''
    Returns an unused localhost port for the pytest session salt minion engine
    '''
    return get_unused_localhost_port()


@pytest.fixture
def secondary_minion_tcp_pub_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_secondary_minion_tcp_pub_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def secondary_minion_tcp_pull_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_secondary_minion_tcp_pull_port():
    '''
    Returns an unused localhost port
    '''
    return get_unused_localhost_port()


@pytest.fixture
def secondary_minion_engine_port():
    '''
    Returns an unused localhost port for the pytest salt secondary minion engine
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_secondary_minion_engine_port():
    '''
    Returns an unused localhost port for the pytest session salt secondary minion engine
    '''
    return get_unused_localhost_port()


@pytest.fixture
def proxy_engine_port():
    '''
    Returns an unused localhost port for the pytest salt proxy engine
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_proxy_engine_port():
    '''
    Returns an unused localhost port for the pytest session salt proxy engine
    '''
    return get_unused_localhost_port()


@pytest.fixture
def syndic_engine_port():
    '''
    Returns an unused localhost port for the pytest salt syndic engine
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_syndic_engine_port():
    '''
    Returns an unused localhost port for the pytest session salt syndic engine
    '''
    return get_unused_localhost_port()


@pytest.fixture
def sshd_port():
    '''
    Returns an unused localhost port to run an sshd server
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def session_sshd_port():
    '''
    Returns an unused localhost port to run a session scoped sshd server
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def log_server_port():
    '''
    Returns an unused localhost port for the pytest logging manager
    '''
    return get_unused_localhost_port()


@pytest.fixture(scope='session')
def salt_log_port(log_server_port):
    '''
    Returns the log_server_port fixture value for backwards compatibility
    '''
    return log_server_port
