#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
#from . import query3
from . import query5
from . import query6
from . import query7
from . import features
from . import thresholds
from . import contexts
from . import status

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
    #return [query3]
    #return [query5]
    return [query7]

'''
@hug.extend_api("/query3")
def dataman2():
    """ Data manager """
    #return [query3]
    return [query6]
'''

@hug.extend_api("/query3")
def dataman2():
    """ Data manager """
    return [query7]


@hug.extend_api("/thresholds")
def threshman():
    """ api per cambiare thresholds """
    return [thresholds]

@hug.extend_api("/contexts")
def contextman():
    """ api per cambiare contexts """
    return [contexts]

@hug.extend_api("/status")
def contextman():
    """ api per verificare lo stato delle serie """
    return [status]



