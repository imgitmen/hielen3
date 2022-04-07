#!/usr/bin/env python
# coding=utf-8
import hug
from . import prototypes, query, features, actions, actionschemata, hls, queue
import falcon

"""
@hug.not_found()
def not_found():

    return {'error': {
                'status': falcon.status.HTTP_NOT_FOUND,
                'description': 'URL is invalid.',
            }}

api = hug.get(on_invalid=hug.redirect.not_found)
"""

@hug.extend_api("/hls")
def getstream():
    return [hls]

@hug.extend_api("/queue")
def getstream():
    return [queue]

@hug.extend_api("/prototypes")
def protoman():
    """ Prototypes manager """
    return [prototypes]

@hug.extend_api("/features")
def featman():
    """ Features manager """
    return [features]

@hug.extend_api("/actions")
def actiman():
    """ Action manager """
    return [actions]

@hug.extend_api("/actionschemata")
def scheman():
    """ Schemata manager """
    return [actionschemata]

@hug.extend_api("/query")
def dataman():
    """ Data manager """
    return [query]

