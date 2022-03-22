#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
import json
from hielen3 import db
from hielen3.utils import JsonValidable, hasher, ResponseFormatter, uuid
from hielen3.feature import HFeature
from hielen3.geje import GeoJSONSchema
from pandas import Series
from marshmallow import Schema, fields
import traceback


class FeaturePropertiesSchema(Schema):
    context = fields.Str(default=None)
    label = fields.Str(default=None)
    description = fields.Str(default=None)
    location = fields.Str(default=None)
    style = fields.Str(default=None)
    status = fields.Str(default=None)
    timestamp = fields.Str(default=None)


def mkpmaponthefly(geometry):

    try:
        lon=geometry['coordinates'][0]
        lat=geometry['coordinates'][1]

        span=0.005
        
        maptempl = {
            "extent": {
                "minlon": min(lon-span,lon+span),
                "minlat": min(lat-span,lat+span),
                "maxlon": max(lon-span,lon+span),
                "maxlat": max(lat-span,lat+span)
            },
            "center": {
                "lon": lon,
                "lat": lat
            },
            "zoom": {
                "default": 14
            },
            "basemapurl": None, 
            "geographic": True,
            "features": None
        }
    except Exception as e:
        return None

    return maptempl


@hug.post("/")
def create_feature(
    prototype,
    properties: JsonValidable(FeaturePropertiesSchema()) = {},
    geometry: JsonValidable(GeoJSONSchema()) = None,
    request=None,
    response=None,
):

    """
DESCRIZIONE:

**Creazione delle Features.**

Ogni feature viene creata sulla  il suo il suo prototipo `prototype` ed in fase di creazione \
viene creato il campo `uid`. Questi due campi sono immutabli. Vedi [PUT feature](#put-featuresuid)

PARAMETRI:

- **prototype**: Definisce il tipo della feature e accetta uno dei valori recuperabili \
attraverso l'API [GET prototype](../prototypes/#get)

- **properties**: Json dei campi anagrafici della feature, utilizzati dal sistema. Nessuno di \
essi è obbligatorio. Lo schema è il seguente:


        {
            "context": "Stringa: gruppo in cui inserire la feature",
            "label":  "Stringa: etichetta mnemonica della feature",
            "description": "Stringa: descrizione della feature",
            "location": "Stringa: descrizione mnemonica della posizioni",
            "style": "Stringa: informazioni per le direttive csv",
            "status": "Stringa: informaizoni di stato",
            "timestamp": "Stringa: data di creazione della feature nel formato YYYY-MM-DD HH:MM:SS"
        }


- **geometry** : Accetta un [GeoJson](https://geojson.org/)

OUTPUT:

Se la feature viene creata correttamente la sua struttura viene restituita all'interno del campo \
`data` del json di risposta standard

RESPONSE CODES:

- _409 Conflict_: Nel caso in cui il uid fornito esista già.
- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _201 Created_: Nel caso in cui la feature venga creata correttamente.
"""
    out = ResponseFormatter(status=falcon.HTTP_CREATED)

    try:

        f = HFeature.create(
                ftype=prototype,
                geometry=geometry,
                **properties
                ).uuid

        #TODO da delegare al plugin specifico se serve
        """
        feature["classification"]=feature_info.pop("classification")
        feature["inmap"]=feature_info.pop("inmap")
        feature_info.update({"data":None, "map":None, "cloud":None})
        """

        out.data=json.loads(db['features'][f].to_json(orient='records'))[0]

        out.data["uid"]=out.data.pop('uuid')

        f=None


    except KeyError as e:
        out.message = f"prototype '{prototype}' not found."
        out.status = falcon.HTTP_NOT_FOUND
    except ValueError as e:
        out.message = e.args
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return


@hug.get("/")
def features_info(uids=None, cntxt=None, info=["geometry","capabilities"], request=None, response=None):
    """
DESCRIZIONE:

**Recupero delle informazioni delle features.**

PARAMETRI:

- **uids**: Lista "comma separated" degli id delle features da recuperare. Nel caso in cui non \
venisse fornito alcun valore, verrebbe fornita in output l'intera lista delle features presenti \
nel sistema.

- **cntxt**: Lista "comma separated" dei gruppi di features da recuperare. Se presente agisce da \
filtro rispetto al risultato elaborato in base al parametro _"uids"_ \

- **info**: Lista "comma separated" delle informazioni relative ad ogni feature da includere nella \
risposta. In generale dei sottoalberi Json. Le classi di informazione disponibili sono:

    - _capabilities_: tipi di interrogazioni eseguibili sulla feature: elenco comprendente una, nessuna \
o più voci tra queste: _data_, _map_, _cloud_. Vedi [GET query](../query/#get)
    - _parameters_: parametri (timeseries) associati alla feature, interrogabili tramite \
[GET query](../query/#get)
    - _timeline_: eventuale timeline globale dei parametri della feature

ESEMPIO:

        GET features?cntxt=619d00137303c&info=parameters,capabilities

OUTPUT:

All'interno del campo `data` del json di risposta standard viene restituito un oggetto \
"chiave, valore" json che é interpretabile come GeoJson estraendo la lista dei values.
L'oggetto contiene tutte le features che rientrano nei criteri di ricerca. Quindi un struttura \
di questo tipo:

	"features": {
		"1285beb4": {
			"type": "Feature",
        		"properties": {
			    "uid": "1285beb4",
			    "classification": "Source",
			    "context": "619d00137303c",
			    "description": null,
			    "label": "CAM1",
			    "location": null,
			    "status": "0",
			    "style": "9cecce36",
			    "timestamp": "2021-11-10 00:00:00",
			    "type": "PhotoMonitoring",
			    "inmap": null
        		},
        		"parameters": [
				{
					"series": "06578ff5509871eef7e62f8d2bc175de",
            				"param": "Displacement",
            				"unit": "mm",
          			},
          			{
            				"series": "2388b145eed5036e78afff43114cf7f7",
            				"param": "Correlation_Coefficient",
            				"unit": "number",
          			},
        		],
        		"timeline": [
		          "2021-11-04T15:11:45"
        		],
        		"capabilities": [
				"map"
			]
      		},
	}
            

RESPONSE CODES:

- _200 OK_: Nel caso vengano trovate features corrispondenti ai criteri di ricerca
- _404 Not Found_: Nel caso in cui nessuna feature risponda ai criteri di ricerca

"""

    out = ResponseFormatter()

    if cntxt is not None and not isinstance(cntxt,list):
        if cntxt == "":
            cntxt = None
        else:
            cntxt = [cntxt]

    if info is None:
        info = []

    if not isinstance(info,list):
        info = [info]

    info.extend(["type","properties","capabilities"])

    info = Series(list(set(info)))

    good_info=info[info.isin(db['features_info'].columns)]
    bad_info=info[~info.isin(db['features_info'].columns)]

    # TODO: GESTIONE DEI SUBITEMS
    """
    if 'map' in info:
        info.append('subitemsfrommap')
    """

    try:
        feafra=db['features_info'][uids,cntxt][good_info]
        feafra[bad_info]=None
        feafra=feafra.where(feafra.notnull(), None)
        feafra=json.loads(feafra.droplevel("context").to_json(orient='index'))
        out.data = { "features":feafra }
        feafra=None

    except KeyError as e:
        out.data = { "features":[] }
        #out.status = falcon.HTTP_NOT_FOUND
        out.message = e.args

    response = out.format(response=response, request=request)

    return


@hug.get("/{uid}")
def feature_info(uid, cntxt=None, info=["geometry","capabilities"], request=None, response=None):
    """
DESCRIZIONE:

**Alias di recupero informazioni della specifica feature**

PARAMETRI:

- **info**: Lista "comma separated" delle informazioni relative ad ogni feature da includere nella \
risposta. In generale dei sottoalberi Json. Le classi di informazione disponibili sono:

    - _capabilities_: tipi di interrogazioni eseguibili sulla feature: elenco comprendente una, nessuna \
o più voci tra queste: _data_, _map_, _cloud_. Vedi [GET query](../query/#get)
    - _parameters_: parametri (timeseries) associati alla feature, interrogabili tramite \
[GET query](../query/#get)
    - _timeline_: eventuale timeline globale dei parametri della feature

ESEMPIO:

        GET features/1285beb4&info=parameters,capabilities

OUTPUT:

Vedi [GET features](#get)


RESPONSE CODES:

- _200 OK_: Nel caso vengano trovate features corrispondenti ai criteri di ricerca
- _404 Not Found_: Nel caso in cui nessuna feature risponda ai criteri di ricerca

"""
    return features_info(uid, cntxt, info, request, response)


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
- _200 Ok_: Nel caso in cui la feature venga modificata correttamente.
"""

    out = ResponseFormatter()

    if uid is None:
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = "None value not allowed"

    try:

        f = HFeature.update(
                uuid=uid,
                geometry=geometry,
                **properties
                ).uuid


        out.data=json.loads(db['features'][f].to_json(orient='records'))[0]

        out.data["uid"]=out.data.pop('uuid')
         
        f=None

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
- _200 Accepted_: Nel caso in cui la feature venga eliminata correttamente.
"""

    #TODO Ottimizzare passando direttamente al db
    out = ResponseFormatter()

    if uid is None:
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = "None value not allowed"

    try:
        out.data=json.loads(db['features'][uid].to_json(orient='records'))[0]
        out.data["uid"]=out.data.pop('uuid')
        HFeature.drop(uuid=uid)

    except KeyError as e:
        #traceback.print_exc()
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{uid}' not foud."
    
    response = out.format(response=response, request=request)

    return
