"""
doctor.py

Defines the Doctor class for managing
a collection of HTTP health checks.
"""

from . import check, report
from rx import timer

import threading
import logging


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
        Mainloop for getting the result of each of the
        doctor's health checks and return a report of
        the complete results.
        """
        self.results = [] # to store check.CheckResult
        self.res_lock = threading.Lock()

        for ch in self.checks:
            timer.PerpetualTimer(float(ch.interval_seconds), ch._run, args=(self.results, self.res_lock,)).start()

        # Create an extra timer for reporting periodically
        timer.PerpetualTimer(2.0, self.__report).start()

    def __report(self):
        self.res_lock.acquire()
        if self.results:
            rep = report.Report(self.results)
            logging.info(str(rep))
            rep.log_failures()
            self.results.clear() # reset results for next report
        self.res_lock.release()


