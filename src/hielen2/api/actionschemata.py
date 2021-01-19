#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen2 import db, source
from himada.api import ResponseFormatter


@hug.get("/")
def get_protos_schemata(prototypes=None,actions=None,request=None, response=None):
    """
**Recupero dello schema dei parametri per inizializare le forms delle azioni**

ritorna una struttura json di questo tipo:


        {
            "NomePrototipo1": {
                "action1": {
                    "args": {
                        "arg1.1": "type_arg1.1",
                        "arg1.2": "type_arg1.2",
                        ...
                    },
                    "mandatory": [ args keys sublist ]
                },
                "action2": {
                    "args": {
                        "arg2.1": "type_arg2.1",
                        "arg2.2": "type_arg2.2",
                        ...
                    },
                },
                ...
            },
            "NomePrototipo3": {
                ...
            },
            ...
        },
"""
    out = ResponseFormatter()

    out.data={}

    try:
        if actions is not None and actions is not list:
            actions=[actions]

        protos=db["features_proto"][prototypes]

        if not isinstance(protos,list):
            protos=[protos]

        for p in protos: 
            uid=p['uid']
            out.data[uid]={}
            for a in [ act for act in source.moduleActions(uid) if actions is None or act in actions ]:
                out.data[uid][a]=source.getActionSchema(uid,a)
    except KeyError as e:
        out.status = out.status = falcon.HTTP_NOT_FOUND
        out.message = str(e)
        raise e
    response = out.format(response=response, request=request)


@hug.get("/{prototype}")
def get_proto_schemata(prototype, actions=None,request=None, response=None):
    """
**Alias per il recupero di tutte le informazioni di uno specifico prototipo**
"""
    return get_protos_schemata(prototype,actions,request,response)

@hug.get("/{prototype}/{action}")
def get_proto_schema(prototype, action, request=None, response=None):
    """
**Alias per il recupero di tutte le informazioni delle form di uno specifico prototipo**
"""
    return get_protos_schemata(prototype,action,request,response)

