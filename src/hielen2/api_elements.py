#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen2 import db
from himada.api import ResponseFormatter


@hug.post('/')
def create_elements(code,prototype,geom=None,request=None,response=None):

    out = ResponseFormatter(status=falcon.HTTP_CREATED)
    try:
        proto= db['prototypes'][prototype]
    except KeyError e:
        out.message=e
        response=out.format(response=response,request=request)
        return


    return "Not Yet Implemented"


def elinfo(el):

    if el is None:
       return None
     
    info={ k:w for k,w in el.items() if k not in ('code',) }

    info['parameters']=[ {'series':e[1],'name':e[0], 'unit': db['series'][e[1]]['mu']} for e in el['parameters'].items() if e[1] is not None ]
     
    return info  


@hug.get('/',examples='')
def elements_info( elist=None, request=None, response=None ):

    return {  k:elinfo(w) for k,w in db['elements'][elist].items() }


@hug.get('/{code}', examples='')
def element_info( code, request=None, response=None ):

    el = db['elements'][code]

    if code is None:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
        out.message=code
        response = out.format(response=response,request=request)
        return

    return  elinfo(el)

