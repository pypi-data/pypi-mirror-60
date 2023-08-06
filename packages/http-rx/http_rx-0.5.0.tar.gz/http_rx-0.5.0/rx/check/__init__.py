"""
Package: rx.check

Defines functions for performing a health
check against a HTTP target.
"""


class Check(object):
    """
    Base class for a generic health check
    against a HTTP target. Minimal required
    `conf` should contain the following keys:
        * `name`    - readable name for the check; defaults to the `type`
        * `type`    - name of the check class to use; defaults to StatusCodeCheck
    """
    def __init__(self, conf):
        self.name = conf.get('name', conf.get('type', self.__repr__()))

    def result(self, response):
        raise NotImplementedError("you must implement the result(self, response) method")

    @staticmethod
    def parse(conf):
        ctype = conf['type']

        # Dynamically obtain the check class to use
        import sys
        try:
            mod_name = __name__
            class_name = ctype

            type_parts = ctype.split('.')
            if len(type_parts) > 1:
                mod_name = '.'.join(type_parts[:-1])
                class_name = type_parts[-1]

            mod = sys.modules[mod_name]
            ch = getattr(mod, class_name)

            # Check is valid and we now have the actual class/type loaded
            # initialize the check and return it to caller
            return ch(conf)
        except (AttributeError, KeyError):
            # The class couldn't be found in this module
            raise KeyError(f'{ctype} is not a valid check type; make sure the class is loaded in your sys.modules')


class StatusCodeCheck(Check):
    """
    Checks the status code of a HTTP response
    to validate expected result.

    Use the `expected` config value to specify
    the expected HTTP response status code;
    defaults to `200` (OK).

    Note: this check is the default type of check
    performed if the `type` key is not specified.
    """
    def __init__(self, conf):
        super().__init__(conf)
        self.expected_status = conf.get('expected', 200) # default to expect 200 (OK)

    def result(self, resp):
        if resp.status_code != self.expected_status:
            fail_msg = f'expected status code {self.expected_status} but got {resp.status_code}'
            return Result(resp=resp, is_healthy=False, fail_reason=fail_msg)
        else:
            return Result(resp=resp, is_healthy=True)


class Result(object):
    """
    Wraps the result of performing a health
    check against a HTTP target.
    """
    def __init__(self, name='', resp=None, is_healthy=True, fail_reason=None):
        self.resp        = resp
        self.is_healthy  = is_healthy
        self.fail_reason = fail_reason
        self.name        = name

    def __str__(self):
        """
        Returns a formatted string containing the reason for failure.
        """
        label = self.name if self.name else self.resp.url

        if self.is_healthy:
            return 'check {label} passed'.format(label=label)
        else:
            return 'check {label} failed : {reason}'.format(label=label, reason=self.fail_reason)


# Import other built-in checks for convenient resolution
from .check_headers import *
