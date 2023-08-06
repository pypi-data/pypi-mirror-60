import pytest
import requests

import re

from . import HeaderCheck, Result


@pytest.fixture
def header_check():
    return HeaderCheck({
        'name': 'test_header_check',
        'headers': {
            'Content-Type': 'text/html',
        }
    })

class TestHeaderCheck:
    def test_create_headercheck(self, header_check):
        assert isinstance(header_check, HeaderCheck)
        assert isinstance(header_check.conditions, dict)
        assert header_check.conditions

    def test_parse_conditions(self):
        conds = HeaderCheck.parse_conditions({
            '   Content-Type  ': 'text/html',
        })
        assert conds == {
            'content-type': re.compile('text/html'),
        }

    def test_headercheck_str(self, header_check):
        assert str(header_check) == '[HeaderCheck] test_header_check'

    def test_headercheck_result(self, header_check):
        fake_resp = requests.Response()
        fake_resp.url = 'http://test.com'
        fake_resp.status_code = 200
        fake_resp.headers = requests.structures.CaseInsensitiveDict({
            'content-type': 'text/html'
        })
        res = header_check.result(fake_resp)
        assert isinstance(res, Result)
        assert res.is_healthy

        fake_resp.headers = requests.structures.CaseInsensitiveDict({
            'content-type': 'application/json'
        })
        res = header_check.result(fake_resp)
        assert not res.is_healthy
        assert "'content-type' did not match expected expression: text/html" in str(res)

        fake_resp.headers = requests.structures.CaseInsensitiveDict()
        res = header_check.result(fake_resp)
        assert not res.is_healthy
        assert "'content-type' was not found in response" in str(res)
