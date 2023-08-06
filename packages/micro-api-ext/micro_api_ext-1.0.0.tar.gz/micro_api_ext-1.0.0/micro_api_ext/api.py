# encoding: utf-8
"""
Extended Api implementation with an application-specific helpers
----------------------------------------------------------------
"""

from micro_restplus_ext.api import Api as BaseApi
from six import iteritems

from .namespace import Namespace


class Api(BaseApi):
    """
    Having app-specific handlers here.
    """

    def namespace(self, *args, **kwargs):
        # The only purpose of this method is to pass custom Namespace class
        _namespace = Namespace(*args, **kwargs)
        self.namespaces.append(_namespace)
        return _namespace

    def add_namespace(self, ns, path=None):
        super(Api, self).add_namespace(ns, path=path)
