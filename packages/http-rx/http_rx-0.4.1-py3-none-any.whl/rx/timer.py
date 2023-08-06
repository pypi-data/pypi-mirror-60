"""
timer.py

Implements perpetual timer utility
to complement the threading.Timer class.
"""

import threading


class PerpetualTimer(object):
    """
    A timer that runs continuously, executing the
    target callable every `seconds` seconds, repeatedly.
    """

    def __init__(self, seconds, target, args=None, kwargs=None):
        self._should_continue = False
        self.is_running = False
        self.seconds = seconds
        self.target = target
        self.thread = None
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}

    def _handle_target(self):
        self.is_running = True
        self.target(*self.args, **self.kwargs)
        self.is_running = False
        self._start_timer()

    def _start_timer(self):
        # Code could have been running when cancel was called.
        if self._should_continue:
            self.thread = threading.Timer(self.seconds, self._handle_target)
            self.thread.start()

    def start(self):
        if not self._should_continue and not self.is_running:
            self._should_continue = True
            self._start_timer()

    def cancel(self):
        if self.thread is not None:
            # Just in case thread is running and cancel fails.
            self._should_continue = False
            self.thread.cancel()
