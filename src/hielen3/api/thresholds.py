#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
import json
from hielen3 import db
from hielen3.utils import JsonValidable, hasher, ResponseFormatter, uuid, dataframe2jsonizabledict
from hielen3.feature import HFeature,HSeries
from pandas import Series
from marshmallow import Schema, fields
import traceback


class ThresholdSchema(Schema):
    label = fields.Str(required=True)
    ttype = fields.Str(required=True)
    value = fields.Number(required=True)
    color = fields.Str(required=False)
    recipients = fields.Str(required=False)


@hug.post("/")
def create_thresholds(
    series,
    thresholds: JsonValidable(ThresholdSchema(many=True)),
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

**Modifica delle soglie.**

PARAMETRI:

- **series**: array di uuid delle serie per cui modificare le soglie 

- **thresholds**: Json dei campi delle soglie. Lo schema è il seguente:


        {
            "label": "Stringa: tipologia di soglia ('Alarm','Alert',...)",
            "ttype":  "Stringa: tipo: Superiore ( 'UPPER' ), inferiore ( 'LOWER' )",
            "value": "Numero: valore della soglia,
            "color": "Stringa: colore della soglia",
            "recipients": "Stringa: 'intesa come elenco di email'"
        }


OUTPUT:

Se la soglia viene creata/modificata correttamente la sua struttura viene restituita all'interno del campo \
`data` del json di risposta standard

RESPONSE CODES:

- _404 Not Found_: Nel caso in cui le serie richieste non esistano.
- _200 OK_: Nel caso in cui la feature venga creata correttamente.
"""
    out = ResponseFormatter(status=falcon.HTTP_OK)

    if not isinstance(series,(list,set,tuple)):
        series=[series]

    try:
        for s in series:
            HSeries(db['series'][s]['uuid'].squeeze()).attribute_update(attribute="thresholds",value=thresholds)
    except KeyError as e:
        out.message = f"series '{s}' not found."
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = e.args
        out.status = falcon.HTTP_CONFLICT
        pass

    response = out.format(response=response, request=request)

    return


@hug.post("/{series}")
def create_spec_thresholds(
    series,
    thresholds,
    request=None,
    response=None,
    **kwargs
):
    return create_thresholds(series,thresholds,request,response,**kwargs)


@hug.get("")
def retrive_thresholds(
    series=None,
    labels=None,
    request=None,
    response=None,
    **kwargs
):

    out = ResponseFormatter(status=falcon.HTTP_OK)

    if isinstance(series,str): series=series.split(",")
    
    if not isinstance(series,(list,set,tuple)) and series is not None:
        series=[series]

    if not series is None: series = [ a for a in series if a is not None and a.__len__()]
    if not series is None and not series.__len__(): series = None
     
    if isinstance(labels,str): labels=labels.split(",")

    if not isinstance(labels,(list,set,tuple)) and labels is not None:
        labels=[labels]

    if not labels is None: labels = [ a for a in labels if a is not None and a.__len__()]
    if not labels is None and not labels.__len__(): labels = None


    #DEBUG print ({"series":series,"labels":labels})

    try:
        out.data=db['series_thresholds'][{"series":series,"label":labels}].to_dict(orient="records")
    except KeyError as e:
        out.message = f"series '{e}' not found."
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = e.args
        out.status = falcon.HTTP_CONFLICT
        pass
 

    response = out.format(response=response, request=request)
     
    return  

@hug.get("/{series}")
def retive_spec_thresholds(
    series,
    labels=None,
    request=None,
    response=None,
    **kwargs
):
    return retrive_thresholds(series,labels,request,response,**kwargs)


@hug.get("/{series}/{labels}")
def retive_spec_thresholds(
    series,
    labels,
    request=None,
    response=None,
    **kwargs
):
    return retrive_thresholds(series,labels,request,response,**kwargs)


