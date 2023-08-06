"""
doctor.py

Defines the Doctor class for managing
a collection of HTTP health checks.
"""

from . import check, report
from .request import Request
from rx import timer

import threading
import logging


class Doctor(object):
    """
    Health check manager for keeping track
    of and reporting on a collection of
    requests and health checks for them.
    """
    def __init__(self, config):
        self.requests = [Request.parse(conf) for conf in config['requests']]
        self.reporting_conf = config.get('report', {})

    def __iadd__(self, new_request):
        """
        Add a new request to the doctor's
        health checklist.
        """
        assert isinstance(new_request, Request)
        self.requests.append(new_request)

    def run(self):
        """
        Mainloop for getting the results of each of the
        doctor's request targets and return a report of
        the complete results.
        """
        self.results = [] # to store check.CheckResult
        self.res_lock = threading.Lock()

        for req in self.requests:
            interval_seconds = float(req.interval)
            if interval_seconds <= 0:
                # Non-positive interval --> one-shot; use normal threading timer
                threading.Timer(float(req.interval), req._run, args=(self.results, self.res_lock,)).start()
            else:
                timer.PerpetualTimer(float(req.interval), req._run, args=(self.results, self.res_lock,)).start()

        # Create an extra timer for reporting periodically
        reporting_interval = self.reporting_conf.get('interval', 5.0)
        assert isinstance(reporting_interval, float)
        timer.PerpetualTimer(reporting_interval, self.__report).start()

    def __report(self):
        self.res_lock.acquire()
        if self.results:
            rep = report.Report(self.results)
            logging.info(str(rep))
            rep.log_failures()
            self.results.clear() # reset results for next report
        self.res_lock.release()


