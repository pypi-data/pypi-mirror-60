import pytest
import requests

from .request import Request


class TestRequest:
    def test_request_parsing(self):
        r = Request.parse({'url': 'http://test.com', 'checks': []})
        assert isinstance(r, Request)
        assert r.url == 'http://test.com'
        assert r.name == '{}:http://test.com'.format(Request.DEFAULT_HTTP_METHOD)
        assert r.interval == Request.DEFAULT_INTERVAL
        assert r.data is None
        assert r.headers == []
        assert r.checks == []
