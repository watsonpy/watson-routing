# -*- coding: utf-8 -*-
from wsgiref import util
from watson.http import messages


def sample_environ(**kwargs):
    environ = {'PATH_INFO': '/'}
    util.setup_testing_defaults(environ)
    environ.update(kwargs)
    return environ


def sample_request(**kwargs):
    environ = sample_environ(**kwargs)
    request = messages.Request(environ)
    return request
