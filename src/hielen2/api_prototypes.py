#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen2 import db
from himada.api import ResponseFormatter


@hug.post('/')
def prots(code,request=None, response=None):
    return "not yet implemented"

@hug.get('/', examples='/')
def prots( request=None, response=None ):
    out=ResponseFormatter()
    try:
        out.data=db['prototypes'].db
    except KeyError as e:
        out.status=out.status=falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response,request=request)


@hug.get('/{eltype}', examples='')
def eltypes(eltype, request=None, response=None):
    out=ResponseFormatter()
    try:
        out.data=db['prototypes'].get(eltype)
    except KeyError as e:
        out.status=out.status=falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response,request=request)

@hug.get('/{eltype}/forms', examples='')
def eltypes(eltype, request=None, response=None):
    out=ResponseFormatter()
    try:
        out.data=db['prototypes'].get(eltype)['forms']
    except KeyError as e:
        out.status=out.status=falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response,request=request)


@hug.get('/{eltype}/forms/{form}', examples='')
def eltypes(eltype, form, request=None, response=None):
    out=ResponseFormatter()
    try:
        out.data=db['prototypes'].get(eltype)['forms'][form]
    except KeyError as e:
        out.status=out.status=falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response,request=request)




