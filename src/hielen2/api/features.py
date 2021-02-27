#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen2 import db
from hielen2.utils import JsonValidable
from marshmallow import Schema, fields
from himada.api import ResponseFormatter
from marshmallow_geojson import GeoJSONSchema


class FeaturePropertiesSchema(Schema):
    context = fields.Str(default="no-context", allow_none=False)
    label = fields.Str(default=None)
    description = fields.Str(default=None)
    location = fields.Str(default=None)
    style = fields.Str(default=None)
    status = fields.Str(default=None)
    timestamp = fields.Str(default=None)


@hug.post("/")
def create_feature(
    uid,
    prototype,
    properties: JsonValidable(FeaturePropertiesSchema()) = {},
    geometry: JsonValidable(GeoJSONSchema()) = {},
    request=None,
    response=None,
):

    """
**Creazione delle Features.**

Ogni feature deve avere il suo codice univoco `uid` e il suo prototipo `prototype`. Questi due \
campi sono immutabli (vedi PUT `/feature/{uid}`).
Il prototipo della feature forisce informazioni per l'inizializazione della struttura.
Il parametro `geometry` deve essere un GeoJson

Se la feature viene creata correttamente ne restituisce la struttura

Possibili risposte:

- _409 Conflict_: Nel caso in cui il uid fornito esista già.
- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _201 Created_: Nel caso in cui la feature venga creata correttamente.
"""

    out = ResponseFormatter(status=falcon.HTTP_CREATED)

    try:
        feature = db["features_proto"][prototype]['struct']

#TODO CREARE SERIES

        feature['parameters']={ k:None for k in feature['parameters'].keys() }

##

        feature["geometry"]= geometry
        feature["uid"] = uid

        try:
            assert properties["context"] is not None
        except Exception:
            properties["context"] = "no-context"


        feature.update(properties)


        db["features"][uid] = feature

        out.data = db["features"][uid]

    except KeyError as e:
        out.message = f"prototype '{prototype}' not found."
        out.status = falcon.HTTP_NOT_FOUND
    except ValueError as e:
        out.message = f"feature '{feature['uid']}' exists"
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)
    return


@hug.get("/")
def features_info(uids=None, cntxt=None, request=None, response=None):

    """
**Recupero delle informazioni delle features.**

__nota__: uids accetta valori multipli separati da virgola 

viene restituito una struttura di questo tipo:


        {
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        ...
                    },
                    "geometry": <GeoJson Validable>
                },
                ...
            ]
        }


___nota___: Al contrario di quanto detto nel TODO non viene inserito il context a livello \
"features" perchè in effetti è una informazione sempre conosciuta a priori (se si lavora \
per commesse). Al contrario se si lavora per uids allora ha senso inserie questa info all' \
interno delle properties delle singole features.


Possibili risposte:

- _404 Not Found_: Nel caso in cui nessuna feature risponda ai criteri
"""

    out = ResponseFormatter()

    try:
        out.data = {"features":[]}
        extract=db["features"][uids]
        if not isinstance(extract,list):
            extract=[extract]
        for v in extract:
            if cntxt is None or v["context"] == cntxt:
                out.data['features'].append({
                    "type": "Feature",
                    "geometry": v.pop("geometry"),
                    "parameters": v.pop("parameters"),
                    "properties": v
                    })
    except KeyError as e:
        out.status = falcon.HTTP_NOT_FOUND
        out.message = str(e)

    response = out.format(response=response, request=request)
    return


@hug.get("/{uid}")
def feature_info(uid, cntxt=None, request=None, response=None):
    """
    **Alias di recupero informazioni della specifica feature**"""
    return features_info(uid, cntxt, request, response)


@hug.put("/{uid}")
def update_feature(
    uid,
    properties: JsonValidable(FeaturePropertiesSchema()) = {},
    geometry: JsonValidable(GeoJSONSchema()) = {},
    request=None,
    response=None,
):
    
    """
**Modifica delle properties di una feature**

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _202 Accepted_: Nel caso in cui la feature venga modificata correttamente.
"""

    out = ResponseFormatter(status=falcon.HTTP_ACCEPTED)

    if uid is None:
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = "None value not allowed"

    try:
        feat = db["features"][uid]
        feat.update(properties)
        feat["geometry"].update(geometry)
        db["features"][uid] = None
        db["features"][uid] = feat
        out.data = db["features"][uid]
    except KeyError as e:
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{uid}' not foud."

    response = out.format(response=response, request=request)
    return


@hug.delete("/{uid}")
def del_feature(uid, request=None, response=None):

    """
**Cancellazione delle Features**

Se la feature viene cancellata correttamente ne restituisce la struttura

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _202 Accepted_: Nel caso in cui la feature venga eliminata correttamente.
"""

    out = ResponseFormatter(falcon.HTTP_ACCEPTED)

    if uid is None:
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = "None value not allowed"

    try:
        out.data = db["features"][uid]
        db["features"][uid] = None
    except KeyError as e:
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{uid}' not foud."

    response = out.format(response=response, request=request)
    return

