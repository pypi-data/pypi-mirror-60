import pytest

import requests

from . import Check, StatusCodeCheck, Result

class TestCheck:
    def test_check_parser(self):
        conf = {
            'type': 'rx.check.StatusCodeCheck',
            'name': 'TestCheck',
            'expected': 201,
        }
        chk = Check.parse(conf)
        assert chk.name == 'TestCheck'
        assert isinstance(chk, Check)
        assert isinstance(chk, StatusCodeCheck)
        assert chk.expected_status == 201

    def test_check_parser_requires_type(self):
        with pytest.raises(KeyError) as err:
            Check.parse({})
        assert 'type' in str(err)

    def test_base_check_class_not_usable(self):
        with pytest.raises(NotImplementedError):
            abstract_check = Check({'type': 'rx.check.Check'})
            abstract_check.result(None)

    def test_check_parsing_defaults_name_to_type(self):
        chk = Check({'type': 'rx.check.Check'})
        assert chk.name == 'rx.check.Check'

    def test_check_parsing_infers_builtin(self):
        chk = Check.parse({'type': 'StatusCodeCheck'})
        assert isinstance(chk, Check)
        assert isinstance(chk, StatusCodeCheck)
        assert chk.expected_status == 200

    def test_check_parsing_throws_error_on_bad_type(self):
        with pytest.raises(KeyError) as err:
            Check.parse({'type': 'some.NonExistentCheck'})
        assert 'some.NonExistentCheck is not a valid check type' in str(err)


class TestResult:
    def test_result_str(self):
        fake_resp = requests.Response()
        fake_resp.url = 'http://test.com'
        res = Result(name='test', resp=fake_resp, is_healthy=False, fail_reason='error')
        assert str(res) == 'check test failed : error'

        res.is_healthy = True
        assert str(res) == 'check test passed'

        res = Result(resp=fake_resp, is_healthy=True, fail_reason='error')
        assert str(res) == 'check http://test.com passed'


class TestStatusCodeCheck:
    def test_status_code_check_result(self):
        fake_resp = requests.Response()
        fake_resp.url = 'http://test.com'
        fake_resp.status_code = 200
        chk = StatusCodeCheck({'expected': 201})
        assert chk.expected_status == 201
        res = chk.result(fake_resp)
        assert not res.is_healthy
        assert 'expected status code 201 but got 200' in str(res)
        fake_resp.status_code = 201
        res = chk.result(fake_resp)
        assert res.is_healthy
