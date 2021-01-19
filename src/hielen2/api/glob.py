#!/usr/bin/env python
# coding=utf-8
import hug
from . import parameters, prototypes, data, features, actions, actionschemata
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


@hug.extend_api("/parameters")
def elemman():
    """ parameters manager """
    return [parameters]


@hug.extend_api("/prototypes")
def protoman():
    """ Prototypes manager """
    return [prototypes]


@hug.extend_api("/data")
def dataman():
    """ Series manager """
    return [data]


@hug.extend_api("/features")
def dataman():
    """ Series manager """
    return [features]


@hug.extend_api("/actions")
def dataman():
    """ Series manager """
    return [actions]

@hug.extend_api("/actionschemata")
def dataman():
    """ Series manager """
    return [actionschemata]
