"""
doctor.py

Defines the Doctor class for managing
a collection of HTTP health checks.
"""

from . import check, report


class Doctor(object):
    """
    Health check manager for keeping track
    of and reporting on a collection of 
    health checks.
    """
    def __init__(self, config):
        self.checks = [check.parse_check(conf) for conf in config['checks']]

    def __iadd__(self, new_check):
        """
        Add a new check to the doctor's 
        healthy checklist.
        """
        assert isinstance(new_check, check.Check)
        self.checks.append(new_check)

    def run(self):
        """
        Get the result of each of the doctor's
        health checks and return a report of 
        the complete results.
        """
        results = [] # to store check.CheckResult

        # TODO: add multi-threading
        for ch in self.checks:
            results.append(ch.result())

        return report.Report(results)


