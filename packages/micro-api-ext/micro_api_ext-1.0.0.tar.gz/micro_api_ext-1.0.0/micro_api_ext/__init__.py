# encoding: utf-8
"""
API extension
=============
"""
# flake8: noqa
from .api import Api
from .namespace import Namespace
from .http_exceptions import abort


def init_app(app, **kwargs):
    # pylint: disable=unused-argument
    """
    API extension initialization point.
    """

    # Prevent config variable modification with runtime changes
    pass
