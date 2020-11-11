#!/usr/bin/env python
# coding=utf-8
import hug
from . import elements, prototypes, data
import falcon

'''
@hug.not_found()
def not_found():

    return {'error': {
                'status': falcon.status.HTTP_NOT_FOUND,
                'description': 'URL is invalid.',
            }}

api = hug.get(on_invalid=hug.redirect.not_found)
'''

@hug.extend_api('/prototypes')
def protoman():
    ''' Prototypes manager '''
    return [prototypes]

@hug.extend_api('/elements')
def elemman():
    ''' Elements manager '''
    return [elements]

@hug.extend_api('/data')
def dataman():
    ''' Series manager '''
    return [data]
