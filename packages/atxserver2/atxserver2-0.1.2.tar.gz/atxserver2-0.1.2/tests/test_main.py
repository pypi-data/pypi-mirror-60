# coding: utf-8
#

import pytest
import atxserver2


@pytest.fixture
def client():
    return atxserver2.Client("http://localhost:4000",
                             "97076434bbbe4dcfb176715e3cad766f")


def test_user(client: atxserver2.Client):
    info = client.user_info()
    assert "username" in info
    assert "email" in info


def test_list_device(client: atxserver2.Client):
    for d in client.list_device():
        d._udid = "xxx"
        d.acquire()
        print(d.atx_agent_address)
        print(d.remote_connect_address)
        d.release()