#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen2 import db
from himada.api import ResponseFormatter


@hug.post("/")
def new_protptype(prototype, request=None, response=None):
    """
    ** Definizione di nuovi prototipi **
    _PLACEHOLDER: Non ancora implementato_"""

    return "not yet implemented"


@hug.get("/")
def prototypes(request=None, response=None):
    """
    **Recupero di tutte le informazioni dei prototipi**

    ritorna una struttura json di questo tipo:


            {
                "NomePrototipo1": {
                    "forms": {
                        "form1": {
                            "args": {
                                "arg1.1": "type_arg1.1",
                                "arg1.2": "type_arg1.2",
                                ...
                            },
                            "mandatory": [ args keys sublist ]
                        },
                        "form2": {
                            "args": {
                                "arg2.1": "type_arg2.1",
                                "arg2.2": "type_arg2.2",
                                ...
                            },
                        },
                        ...
                    },
                    "module": subclass of hielen2.datalink.HilenSource,
                    "struct": {
                        "parameters": {
                            "param1": {
                                "operands": {
                                    "output": "parameter1 name"
                                },
                                "type": "series type"
                            },
                            "param2": {
                                "operands": {
                                    "output": "parameter2 name"
                                },
                                "type": "series type"
                            },
                            ...
                        },
                        "properties": {
                            "classification": feature classification,
                            "type": feature type
                        }
                    }
                },
                "NomePrototipo3": {
                    ...
                },
                ...
            },

    """
    out = ResponseFormatter()
    try:
        out.data = db["features_proto"][None]
    except KeyError as e:
        out.status = out.status = falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response, request=request)


@hug.get("/{prototype}")
def protptype(prototype, request=None, response=None):
    """
    **Alias per il recupero di tutte le informazioni di uno specifico prototipo**"""
    out = ResponseFormatter()
    try:
        out.data = db["features_proto"][prototype]
    except KeyError as e:
        out.status = out.status = falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response, request=request)


@hug.get("/{prototype}/forms")
def prototype_forms(prototype, request=None, response=None):
    """
    **Alias per il recupero di tutte le informazioni delle form di uno specifico prototipo**"""
    out = ResponseFormatter()
    try:
        out.data = db["features_proto"][prototype]["forms"]
    except KeyError as e:
        out.status = out.status = falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response, request=request)


@hug.get("/{prototype}/forms/{form}")
def prototype_form(prototype, form, request=None, response=None):
    """
    **Alias per il recupero di tutte le informazioni di una specifica form di uno specifico prototipo**"""
    out = ResponseFormatter()
    try:
        out.data = db["features_proto"][prototype]["forms"][form]
    except KeyError as e:
        out.status = out.status = falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response, request=request)


@hug.get("/{prototype}/struct")
def prototype_struct(prototype, request=None, response=None):
    """
**Alias per il recupero delle info di inizializzazione delle features legate ad uno specifico \
prototipo**
"""
    out = ResponseFormatter()
    try:
        out.data = db["features_proto"][prototype]["struct"]
    except KeyError as e:
        out.status = out.status = falcon.HTTP_NOT_FOUND
        out.message = str(e)
    response = out.format(response=response, request=request)
