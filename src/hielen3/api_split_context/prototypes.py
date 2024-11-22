#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen3 import db
from hielen3.utils import ResponseFormatter


@hug.get("/")
def prototypes(request=None, response=None):
    """
**Ritorna l'elenco dei prototipi disponibili come array json**

"""
    out = ResponseFormatter()
    try:
        out.data = list(db['features_proto'].db.index)
    except KeyError as e:
        out.status = out.status = falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response, request=request)


@hug.get("/{prototype}")
def prototype_struct(prototype, request=None, response=None):
    """
**Ritorna informazioni dettagliate sullo specifico prototipo**
"""
    out = ResponseFormatter()
    try:
        out.data = db["features_proto"][prototype]
    except KeyError as e:
        out.status = out.status = falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response, request=request)
