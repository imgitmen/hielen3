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
- _201 Created_: Nel caso in cui la feature venga creata correttamente.
"""
    out = ResponseFormatter(status=falcon.HTTP_CREATED)

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
    
