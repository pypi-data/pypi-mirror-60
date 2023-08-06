import pytest
import requests

from . import report, check


def make_result(is_healthy, failure_reason=None):
    fake_resp = requests.Response()
    fake_resp.url = 'http://test.com'
    fake_resp.status_code = 200

    return check.Result(
        name='test',
        resp=fake_resp,
        is_healthy=is_healthy,
        fail_reason=failure_reason,
    )

@pytest.fixture
def rep():
    r1 = make_result(True)
    r2 = make_result(False, 'error 1')
    r3 = make_result(False, 'error 2')
    return report.Report([r1, r2, r3])


class TestReport:
    def test_creating_report(self, rep):
        assert 'healthy' in rep.results
        assert 'failed' in rep.results
        assert rep.results['healthy'].__len__() == 1
        assert rep.results['failed'].__len__() == 2

    def test_report_str(self, rep):
        assert str(rep) == '1/3 passed (33.33%)'

