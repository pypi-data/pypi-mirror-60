"""
request.py

Defines a atomic HTTP request target for
HTTP RX to perform. A single request can
contain many health checks to be performed
on its results.
"""

import logging

from . import check

import requests


def parse_request(req_conf):
    url = req_conf['url']
    http_method = req_conf.get('method', 'GET')
    name = req_conf.get('name', f'{http_method}:{url}')
    interval = req_conf.get('intervalSeconds', 5.0)
    data = req_conf.get('data', None)
    headers = req_conf.get('headers', [])
    checks = [check.parse_check(conf) for conf in req_conf['checks']]
    return Request(name, http_method, url, interval, data, headers, checks)


class Request(object):
    def __init__(self, name, http_method, url, interval, data, headers, checks):
        self.name = name
        self.http_method = http_method
        self.url = url
        self.interval = interval
        self.data = data
        self.headers = headers
        self.checks = checks

    def _run(self, results, res_lock):
        # Perform the HTTP request and then pass the results to
        # each health check so it can perform its job and respond
        resp = requests.request(
            self.http_method,
            headers=self.headers,
            url=self.url,
            data=self.data
        )
        new_results = [ch.result(resp) for ch in self.checks]
        res_lock.acquire()
        results += new_results
        res_lock.release()


