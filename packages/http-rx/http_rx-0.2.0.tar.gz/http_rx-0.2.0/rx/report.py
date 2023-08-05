"""
report.py

Defines reporting functionality for 
HTTP RX checks/healthiness.
"""

import logging

from . import check


class Report(object):
    """
    Statistics for a collection of health
    check results, including reasons for failures.
    """
    def __init__(self, check_results):
        # check_results is a list of check.CheckResult
        healthy_results = list(filter(lambda res: res.is_healthy, check_results))
        failed_results = list(filter(lambda res: not res.is_healthy, check_results))
        self.results = {
                'healthy': healthy_results,
                'failed' : failed_results,
        }

    def __str__(self):
        healthy = len(self.results['healthy'])
        total   = len(self.results['failed']) + healthy
        healthy_percentage = float(healthy) / float(total) * 100.0
        return f'{healthy}/{total} passed ({healthy_percentage}%)'

    def log_failures(self):
        """
        Log the reason for failure for each 
        failure in the report, if any.
        """
        for failure in self.results['failed']:
            logging.info(failure.failure_str())



