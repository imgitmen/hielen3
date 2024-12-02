#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from . import query2
from . import features
from . import thresholds
from . import contexts

"""
@hug.not_found()
def not_found():

    return {'error': {
                'status': falcon.status.HTTP_NOT_FOUND,
                'description': 'URL is invalid.',
            }}

api = hug.get(on_invalid=hug.redirect.not_found)
"""

@hug.extend_api("/features")
def featman():
    """ Features manager """
    return [features]

@hug.extend_api("/query2")
def dataman2():
    """ Data manager """
    return [query2]

@hug.extend_api("/thresholds")
def threshman():
    """ api per cambiare thresholds """
    return [thresholds]

@hug.extend_api("/contexts")
def contextman():
    """ api per cambiare contexts """
    return [contexts]



