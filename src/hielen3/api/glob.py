#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from . import prototypes
from . import query
from . import query2
from . import features
from . import actions
from . import actionschemata
from . import hls
from . import queue
from . import status
from . import awskine
from . import italferdatarate
from . import thresholds
from . import contexts
from . import contextsroots 

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
def dataman2():
    """ Data manager """
    return [query2]

@hug.extend_api("/status")
def statman():
    """ Data manager """
    return [status]

@hug.extend_api("/thresholds")
def threshman():
    """ api per cambiare thresholds """
    return [thresholds]

@hug.extend_api("/contexts")
def contextman():
    """ api per cambiare contexts """
    return [contexts]

@hug.extend_api("/contextsroots")
def contextman():
    """ api per recuperare la root dei contexts """
    return [contextsroots]

@hug.extend_api("/awskineresources")
def kineresman():
    """ api per aws kinemetrics """
    return [awskine]
 
@hug.extend_api("/samplerate")
def sampleman():
    """ api per cambiare il samplerate """
    return [italferdatarate]



