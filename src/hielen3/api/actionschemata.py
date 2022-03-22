#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen3 import db
from hielen3.feature import HFeature
from hielen3.utils import ResponseFormatter


@hug.get("/")
def get_actions_schemata(prototypes=None,actions=None,request=None, response=None):
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

    try:
        out.data=HFeature.actions_schemata(prototypes,actions)
    except KeyError as e:
        out.data={}
        #out.status = out.status = falcon.HTTP_NOT_FOUND
        out.message = e.args

    response = out.format(response=response, request=request)


@hug.get("/{prototype}")
def get_action_schemata(prototype, actions=None,request=None, response=None):
    """
**Alias per il recupero di tutte le informazioni di uno specifico prototipo**
"""
    return get_actions_schemata(prototype,actions,request,response)

@hug.get("/{prototype}/{action}")
def get_action_schema(prototype, action, request=None, response=None):
    """
**Alias per il recupero di tutte le informazioni delle form di uno specifico prototipo**
"""
    return get_actions_schemata(prototype,action,request,response)

