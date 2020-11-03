#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen2 import db
from himada.api import ResponseFormatter


@hug.post('/')
def new_protptype(prototype,request=None, response=None):
    return "not yet implemented"

@hug.get('/', examples='/')
def prototypes(request=None, response=None ):
    out=ResponseFormatter()
    try:
        out.data=db['prototypes'][None]
    except KeyError as e:
        out.status=out.status=falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response,request=request)


@hug.get('/{prototype}', examples='')
def protptype(prototype, request=None, response=None):
    out=ResponseFormatter()
    try:
        out.data=db['prototypes'][prototype]
    except KeyError as e:
        out.status=out.status=falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response,request=request)

@hug.get('/{prototype}/forms', examples='')
def prototype_forms(eltype, request=None, response=None):
    out=ResponseFormatter()
    try:
        out.data=db['prototypes'][protoypes]['forms']
    except KeyError as e:
        out.status=out.status=falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response,request=request)


@hug.get('/{prototype}/forms/{form}', examples='')
def prototype_form(prototype, form, request=None, response=None):
    out=ResponseFormatter()
    try:
        out.data=db['prototypes'][prototype]['forms'][form]
    except KeyError as e:
        out.status=out.status=falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response,request=request)




