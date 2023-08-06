"""
check_headers.py

Defines health checkers for
validating response header values.
"""

from . import Check, Result

import re

class HeaderCheck(Check):
    def __init__(self, conf):
        super().__init__(conf)
        headersConf = conf.get('headers', {})
        assert isinstance(headersConf, dict)
        self.conditions = self.__class__.parseConditions(headersConf)

    def result(self, resp):
        # Validate each header condition
        for header, expr in self.conditions.items():
            header_val = resp.headers.get(header, None)
            if header_val is None:
                print(resp.headers)
                return self.__failure(resp, f'\'{header}\' was not found in response')
            else:
                if expr.match(header_val) is None:
                    # Did not match configured regular expression --> fail
                    return self.__failure(resp, f'\'{header}\' did not match expected expression: {expr.pattern}')

        # All conditions passed --> success
        return self.__success(resp)

    def __failure(self, resp, fail_reason):
        return Result(
            name=str(self),
            resp=resp,
            is_healthy=False,
            fail_reason=fail_reason,
        )

    def __success(self, resp):
        return Result(
            name=str(self),
            resp=resp,
            is_healthy=True,
        )

    def __str__(self):
        return f'[{self.__class__.__name__}] {self.name}'


    @staticmethod
    def parseConditions(headersConf):
        """
        Parses a dictionary of header conditions.
        The keys of the dictionary are the header names,
        while values are expressions for the condition.

        Expressions are interpreted as Python regex.
        """
        conds = {}
        for header, expr in headersConf.items():
            conds[header.lower().strip()] = re.compile(expr)
        return conds
