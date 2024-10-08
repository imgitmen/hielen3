#!/usr/bin/env python
# coding=utf-8
import hug
from . import prototypes, query, query2, features, actions, actionschemata, hls, queue, status, awskine, italferdatarate, thresholds, thresholds_v2
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

@hug.extend_api("/query2")
def dataman():
    """ Data manager """
    return [query2]

@hug.extend_api("/status")
def dataman():
    """ Data manager """
    return [status]

@hug.extend_api("/awskineresources")
def dataman():
    """ api per aws kinemetrics """
    return [awskine]
 
@hug.extend_api("/samplerate")
def dataman():
    """ api per cambiare il samplerate """
    return [italferdatarate]

@hug.extend_api("/thresholds")
def dataman():
    """ api per cambiare thresholds """
    return [thresholds]

@hug.extend_api("/thresholds2")
def dataman():
    """ api per cambiare thresholds """
    return [thresholds_v2]



