# encoding: utf-8
"""
Webargs Parser wrapper module
-----------------------------
"""
import logging

from webargs.flaskparser import FlaskParser

from .http_exceptions import abort


class CustomWebargsParser(FlaskParser):
    """
    This custom Webargs Parser aims to overload :meth:``handle_error`` in order
    to call our custom :func:``abort`` function.

    See the following issue and the reated PR for more details:
    https://github.com/sloria/webargs/issues/122
    """

    def handle_error(self, error, *args, **kwargs):
        """
        Handles errors during parsing. Aborts the current HTTP request and
        responds with a 422 error.
        """
        status_code = getattr(error, 'status_code', self.DEFAULT_VALIDATION_STATUS)
        msg = list()
        if type(error.messages) is dict:
            for key, value in error.messages.items():
                if isinstance(value, dict):
                    for _key, value in value.items():
                        temp = {'key': "{}/{}".format(key, _key), 'value': value[0]}
                        msg.append(temp)
                if isinstance(value, list):
                    temp = {'key': key, 'value': value[0]}
                    msg.append(temp)
        logging.info(type(error.messages))
        abort(status_code, messages=msg)
