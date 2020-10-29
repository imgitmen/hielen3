#!/usr/bin/env python
# coding=utf-8
import hug
from . import api_elements, api_prototypes, api_series
import falcon

'''
@hug.not_found()
def not_found():

    return {'error': {
                'status': falcon.status.HTTP_NOT_FOUND,
                'description': 'URL is invalid.',
            }}
'''

#api = hug.get(on_invalid=hug.redirect.not_found)

@hug.extend_api('/prototypes')
def dta_api():
    ''' Prototypes manager '''
    return [api_prototypes]

@hug.extend_api('/elements')
def dta_api():
    ''' Elements manager '''
    return [api_elements]

@hug.extend_api('/series')
def dta_api():
    ''' Series manager '''
    return [api_series]
