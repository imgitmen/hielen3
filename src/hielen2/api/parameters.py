#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen2 import db
from hielen2.utils import JsonValidable
from marshmallow import Schema, fields
from himada.api import ResponseFormatter


@hug.get('/',examples='')
def features_params( cntxt=None, uids=None, params=None, request=None, response=None ):
    """
**Ricerca dei parametri associati alle features**.

__nota__: uid accetta valori multipli separati da virgola 

viene restituito una struttura di questo tipo:

        {
            "<fetUID>":[
                {
                    "series":"<series_UID>",
                    "param":"<param_name>",
                    "um":"<mearurement_unit>"
                }
                ...
            ]
            ...
        }


Possibili risposte:

- _404 Not Found_: Nel caso in cui nessun parametro risponda ai criteri



"""


    def _format(ft,params=None):

        if ft is None:
           return []
         
        parameters = []

        if not isinstance(params,(list,set)) and params is not None:
            params=[params]

        try:
            for param,series in ft['parameters'].items():
                if series is not None and params is None or param in params:
                    parameters.append(
                            {
                                'series':series,
                                'name':param,
                                'unit': db['series'][series]['mu']
                            }
                    )
        except AttributeError as e:
            pass
        except TypeError as e: 
            pass

        return parameters


    out = ResponseFormatter()

    if not isinstance(uids,(list,set)) and uids is not None:
        uids=[uids]

    try:
        out.data={ k:_format(w,params) for k,w in db['features'][uids].items() 
                if cntxt is None or w['properties']['context']==cntxt }
    except KeyError as e:
        out.status=falcon.HTTP_NOT_FOUND
        out.message=(str(e))

    response = out.format(response=response,request=request)

    return

@hug.get('/{cntxt}')
def context_features_params( cntxt=None, uids=None, params=None, request=None, response=None ):
    """
**Alias di ricerca dei Parametri nello lo specifico contesto**
"""
    return features_params(cntxt,uids,params,request,response)


@hug.get('/{cntxt}/{uid}')
def context_feature_params( cntxt=None, uid=None, params=None, request=None, response=None ):
    """
**Alias di ricerca dei Parametri della specifica Feature lo specifico contesto**
"""
    return features_params(cntxt,uid,params,request,response)


@hug.get('/{cntxt}/{uid}/{param}')
def context_feature_params( cntxt=None, uid=None, param=None, request=None, response=None ):
    """
**Alias di ricerca dello specifico Parametro della specifica Feature lo specifico contesto**
"""
    return features_params(cntxt,uid,param,request,response)
    
    


