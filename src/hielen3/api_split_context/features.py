#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
import json
from hielen3 import db
from hielen3.feature import HFeature
from hielen3.geje import GeoJSONSchema
from hielen3.utils import JsonValidable
from hielen3.utils import hasher
from hielen3.utils import ResponseFormatter
from hielen3.utils import uuid
from hielen3.utils import dataframe2jsonizabledict
from hielen3.utils import clean_input
from hielen3.utils import boolenize 
from hielen3.contextmanager import lineages
from hielen3.contextmanager import manage_feature_context
from hielen3.contextmanager import detouch_feature_context
from hielen3.contextmanager import remove_feature_context_geometry
from hielen3.contextmanager import feature_in_family
from hielen3.contextmanager import contexts_features_visibility 
from numpy import nan
from pandas import Series
from marshmallow import Schema, fields
from sqlalchemy.exc import IntegrityError
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
        try:
            cntxt=properties.pop("context")
        except KeyError as e:
            cntxt=None

        cntxt=clean_input(cntxt)
    
        if cntxt.__len__() > 1:
            raise ValueError ("cntxt has to be exactly one")

        f = HFeature.create(
                ftype=prototype,
                **properties
                )

        fuid=f.uuid

        if cntxt.__len__(): 
            cntxt=cntxt[0]

            manage_feature_context(feature=fuid,target=cntxt,geometry=geometry)

        f = None

        return feature_info(uid=fuid,cntxt=cntxt,request=request,response=response)

    except KeyError as e:
        out.message = f"prototype '{prototype}' not found."
        out.status = falcon.HTTP_NOT_FOUND
    except ValueError as e:
        out.message = e.args
        out.status = falcon.HTTP_CONFLICT
    except IntegrityError as e:
        out.message = e.args
        out.status = falcon.HTTP_BAD_REQUEST

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

    try:
        uids=clean_input(uids)
        cntxt=lineages(clean_input(cntxt),homo_only=True)
        info=clean_input(info)
        info.extend(["type","properties","capabilities"])

        info = Series(list(set(info)))

        good_info=info[info.isin(db['features_info_v2'].columns)]
        bad_info=info[~info.isin(db['features_info_v2'].columns)]

        # TODO: GESTIONE DEI SUBITEMS
        """
        if 'map' in info:
            info.append('subitemsfrommap')
        """

        feafra=db['features_info_v2'][uids,cntxt][good_info].sort_index(level=["label"]).reset_index('label')
        feafra[bad_info]=None
        feafra=feafra.where(feafra.notnull(), None)

        #feafra=feafra[feafra['intent'] != 'HIDDEN']

        #feafra=feafra.join(feafra['properties'].apply(Series)['label']).sort_values('label')


        #feafra=json.loads(feafra.droplevel("context").to_json(orient='index'))
        feafra=dataframe2jsonizabledict(feafra.droplevel("context"),orient='index',squeeze=False)
        #feafra=dataframe2jsonizabledict(feafra,orient='records',squeeze=False)

        out.data = { "features":feafra, "count":feafra.__len__() }
        feafra=None

    except ValueError as e:
        #raise e
        out.message =  f"some feature belong to multiple non homogeneous contexts: features: {uids} contexts: {cntxt}"

    except KeyError as e:
        out.data = { "features":[], "count":0 }
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
        try:
            cntxt=properties.pop("context")
        except KeyError as e:
            cntxt=None

        cntxt=clean_input(cntxt)
    
        if cntxt.__len__() > 1:
            raise ValueError ("cntxt has to be exactly one")

        f = HFeature.update(
                uuid=uid,
                **properties
                )

        fuid=f.uuid

        if cntxt.__len__(): 
            cntxt=cntxt[0]
            manage_feature_context(feature=fuid,target=cntxt,geometry=geometry)

        f = None

        return feature_info(uid=fuid,cntxt=cntxt,request=request,response=response)
         

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
- _200 OK_: Nel caso in cui la feature venga eliminata correttamente.
"""

    #TODO Ottimizzare passando direttamente al db
    out = ResponseFormatter()

    if uid is None:
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = "None value not allowed"

    try:
        #out.data=json.loads(db['features'][uid].to_json(orient='records'))[0]
        out.data=dataframe2jsonizabledict(db['features'][uid])
        out.data["uid"]=out.data.pop('uuid')
        HFeature.drop(uuid=uid)

    except KeyError as e:
        #traceback.print_exc()
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{uid}' not foud."
    
    response = out.format(response=response, request=request)

    return


@hug.get("/{uid}/status")
def features_status(uid=None, cntxt=None, request=None, response=None):

    out = ResponseFormatter()

    cntxt = clean_input(cntxt)

    uid =  clean_input(uid)

    try:
            
        feafra=db['status_v2'][uid,cntxt].droplevel("context")

        feafra=feafra[~feafra.index.duplicated()]

        feafra=dataframe2jsonizabledict(feafra,orient='records',squeeze=False)

        out.data = feafra

        feafra=None

    except KeyError as e:
        out.data = []
        out.message = e.args

    response = out.format(response=response, request=request)

    return


@hug.get("/{uid}/context")
def get_feature_contexts(
    uid,
    cntxt=None,
    homogeneous=None,
    request=None,
    response=None):

    """
**Restituisce dei contesti  delle Features**

Possibili risposte:

- _404 Not Found_: Nel caso in cui la feature richiesto non esista.
- _200 OK_: In tutti gli altri casi.
"""
    out = ResponseFormatter()

    try:
        uid=clean_input(uid)
        
        if not uid.__len__():
            raise ValueError ("uid is void")
    
        if uid.__len__() > 1:
            raise ValueError ("uid has to be exactly one")

        uid=uid[0]

        cntxt=clean_input(cntxt)

        homogeneous=boolenize(homogeneous,nonevalue=True)
        
        out.data=feature_in_family(feature=uid,contexts=cntxt,homo_only=homogeneous)

    except Exception as e:
        #raise e
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"errors: {e}"
    
    response = out.format(response=response, request=request)


@hug.get("/{uid}/context/{cntxt}")
def get_feature_contexts_endpoint(
    uid,
    cntxt=None,
    homogeneous=None,
    request=None,
    response=None):

    """
**Modifica dei contesti  delle Features**

ALIAS PER GET /{uid}/context

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _200 OK_: Nel caso in cui la feature venga eliminata correttamente.
"""

    return get_feature_contexts(uid=uid,cntxt=cntxt,homogeneous=homogeneous,request=request,response=response)
    

@hug.post("/{uid}/context")
def change_context(
    uid,
    cntxt,
    geometry: JsonValidable(GeoJSONSchema()) = None,
    request=None,
    response=None):

    """
**Modifica dei contesti  delle Features**

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _200 OK_: Nel caso in cui la feature venga eliminata correttamente.
"""

    out = ResponseFormatter()

    try:
        uid=clean_input(uid)
        
        if not uid.__len__():
            raise ValueError ("uid is void")
    
        if uid.__len__() > 1:
            raise ValueError ("uid has to be exactly one")

        uid=uid[0]

        cntxt=clean_input(cntxt)
        
        if not cntxt.__len__():
            raise ValueError ("cntxt is void")
    
        if cntxt.__len__() > 1:
            raise ValueError ("cntxt has to be exactly one")

        cntxt=cntxt[0]

        try:
            db["context"][cntxt]
        except KeyError as e:
            raise ValueError(f"{cntxt} does not exists")

        manage_feature_context(feature=uid,target=cntxt,geometry=geometry)

    except Exception as e:
        #raise e
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"errors: {e}"
    
    response = out.format(response=response, request=request)

    return

@hug.post("/{uid}/context/{cntxt}")
def change_context_enpoint(
    uid,
    cntxt,
    geometry: JsonValidable(GeoJSONSchema()) = None,
    request=None,
    response=None):

    """
**Modifica dei contesti  delle Features**

ALIAS PER POST /{uid}/context

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _200 OK_: Nel caso in cui la feature venga eliminata correttamente.
"""

    return change_context(uid=uid,cntxt=cntxt,geometry=geometry,request=request,response=response) 


@hug.delete("/{uid}/context")
def delete_feature_context(
    uid,
    cntxt,
    request=None,
    response=None):

    """
**Eliminazione di una feature da uno specifico contesto**

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _200 OK_: Nel caso in cui la feature venga eliminata correttamente.
"""
 
    out = ResponseFormatter()

    try:
        uid=clean_input(uid)
        
        if not uid.__len__():
            raise ValueError ("uid is void")
    
        if uid.__len__() > 1:
            raise ValueError ("uid has to be exactly one")

        uid=uid[0]

        cntxt=clean_input(cntxt)
        
        if not cntxt.__len__():
            raise ValueError ("cntxt is void")
    
        if cntxt.__len__() > 1:
            raise ValueError ("cntxt has to be exactly one")

        cntxt=cntxt[0]

        try:
            db["context"][cntxt]
        except KeyError as e:
            raise ValueError(f"{cntxt} does not exists")

        out.data=detouch_feature_context(feature=uid,context=cntxt)

    except Exception as e:
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"errors: {e}"
    
    response = out.format(response=response, request=request)

    return

@hug.delete("/{uid}/context/{cntxt}")
def delete_feature_context_enpoint(
    uid,
    cntxt,
    request=None,
    response=None):

    """
**Eliminazione di una feature da uno specifico contesto**

ALIAS PER DELETE /{uid}/context

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _200 OK_: Nel caso in cui la feature venga eliminata correttamente.
"""

    return delete_feature_context(uid=uid,cntxt=cntxt,request=request,response=response) 

@hug.get("/{uid}/context/{cntxt}/visibility")
def get_feature_contexts_visibility(
    uid=None,
    cntxt=None,
    orphans=None,
    request=None,
    response=None):
    """
DESCRIZIONE:

**Per ogni feature restituisce i path delle famiglie omogenee limitati ai context in ingresso, intesi come radici** 

PARAMETRI:

- **uid**: Lista "comma separated" degli id delle features da recuperare. Nel caso in cui non \
venisse fornito alcun valore, verrebbe fornita in output l'intera lista delle features presenti \
nel sistema.

- **cntxt**: Lista "comma separated" dei contesti radice per cui recuperare le features. Se presente agisce da \
filtro rispetto al risultato elaborato in base al parametro _"uid"_ \

- **orphans**: booleano che espande il filtro cntxt inserendo nel risultato anche le feature "orfane" \
e limita il filtro su _"uid"_. Default = TRUE

ESEMPIO:

        GET features//context//visibility?orphans=False

OUTPUT:

All'interno del campo `data` del json di risposta standard viene restituito un oggetto \
"chiave, valore" json che é interpretabile come Json estraendo la lista dei values.
L'oggetto contiene tutte le features che rientrano nei criteri di ricerca associate alle proprie famiglie omogenee. \
Quindi un struttura \
di questo tipo:

    "features": [
      { /* PRIMA FEATURE */
        "feature": "c29008e9-2cd2-45ca-aeec-23e4e84afcc0",
        "label": "FA-C3S-TR1M-CE6D",
        "contexts": [
          [ /* PRIMA FAMIGLIA OMOGENEA DELLA PRIMA FEATURE */
            {
              "ID": "UUID-Roma",
              "label": "Roma",
              "description": null,
              "actual": true /* CONTESTO A CUI LA FEATURE E' DIRETTAMENTE LINKATA */
            },
            {
              "ID": "UUID-Latium",
              "label": "Latium",
              "description": null,
              "actual": false /* VISIBILE MA ASSOCIATA AD UN CONTESTO DISCENDENTE (UUID-Roma)*/
            }
          ],
          [ /* SECONDA FAMIGLIA OMOGENEA DELLA PRIMA FEATURE */
            {
              "ID": "UUID-Sardinia",
              "label": "Sardinia",
              "description": null,
              "actual": true
            },
            {
              "ID": "UUID-Italy",
              "label": "Italy",
              "description": null,
              "actual": false
            }
          ]
        ]
      },
      { /* SECONDA FEATURE */
        "feature": "e0783e99-8361-4bed-b73f-81845a367487",
        "label": "PO-C7N-TR1M-DAC7",
        "contexts": [
          [
            {
              "ID": "UUID-Roma",
              "label": "Roma",
              "description": null,
              "actual": true
            },
            {
              "ID": "UUID-Latium",
              "label": "Latium",
              "description": null,
              "actual": false
            }
          ]
        ]
      }
    ]
            

RESPONSE CODES:

- _200 OK_: 

"""

    out = ResponseFormatter()

    try:
        uid=clean_input(uid)
        
        cntxt=clean_input(cntxt)

        orphans = boolenize(orphans,True)

        outframe=contexts_features_visibility(features=uid,contexts=cntxt,orphans=orphans).reset_index()

        out.data = {
                "count":outframe.__len__(),
                "features":outframe.sort_values("label").to_dict(orient="records")
                }

    except Exception as e:
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"errors: {e}"
    
    response = out.format(response=response, request=request)

    return

    

@hug.get("/{uid}/geometry")
def get_feature_geometry(
    uid,
    cntxt=None,
    request=None,
    response=None
        ):
    """
**Recupero delle geometry delle features associate ai contesti**

- _404 Not Found_: Nel caso le feature richiesta non esistano nei contesti richiesti.
- _200 OK_: Nel caso in cui la feature venga eliminata correttamente.
"""
    out = ResponseFormatter()

    try:
        uid=clean_input(uid)
        
        cntxt=clean_input(cntxt)

        try:
            fcon=db["context_feature"][{"feature":uid,"context":cntxt}]
        except Exception as e:
            raise ValueError(  f"feature {uid} not found in context {cntxt}" )


        geom=db["geometry"][list(fcon["geometry"])]

        fcongeo=fcon.set_index("geometry").join(geom).drop("uuid",axis=1).set_index("feature")
        
        out.data=fcongeo.groupby("feature").apply(lambda x: x.replace(nan,None).to_dict(orient="records")).to_dict()
    except Exception as e:
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"errors: {e}"
    
    response = out.format(response=response, request=request)

    return

@hug.get("/{uid}/geometry/{cntxt}")
def get_feature_geometry_enpoint(
    uid,
    cntxt=None,
    request=None,
    response=None
        ):
    """
**Recupero delle geometry delle features associate ai contesti**

- _404 Not Found_: Nel caso le feature richiesta non esistano nei contesti richiesti.
- _200 OK_: Nel caso in cui la feature venga eliminata correttamente.
"""
    return get_feature_geometry(uid=uid,cntxt=cntxt,request=request,response=response)
    


@hug.delete("/{uid}/geometry")
def delete_feature_context_geometry(
    uid,
    cntxt,
    request=None,
    response=None):

    """
**Eliminazione della gemoetry di una feature da uno specifico contesto**

- _404 Not Found_: Nel caso la feature richiesta non esista.
- _200 OK_: Nel caso in cui la feature venga eliminata correttamente.
"""
 
    out = ResponseFormatter()

    try:
        uid=clean_input(uid)
        
        if not uid.__len__():
            raise ValueError ("uid is void")
    
        if uid.__len__() > 1:
            raise ValueError ("uid has to be exactly one")

        uid=uid[0]

        cntxt=clean_input(cntxt)
        
        if not cntxt.__len__():
            raise ValueError ("cntxt is void")
    
        if cntxt.__len__() > 1:
            raise ValueError ("cntxt has to be exactly one")

        cntxt=cntxt[0]

        try:
            db["context"][cntxt]
        except KeyError as e:
            raise ValueError(f"{cntxt} does not exists")

        out.data=remove_feature_context_geometry(feature=uid,context=cntxt)

    except Exception as e:
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"errors: {e}"
    
    response = out.format(response=response, request=request)

    return

@hug.delete("/{uid}/geometry/{cntxt}")
def delete_feature_context_geometry_enpoint(
    uid,
    cntxt,
    request=None,
    response=None):

    """
**Eliminazione di una feature da uno specifico contesto**

ALIAS PER DELETE /{uid}/context

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _200 OK_: Nel caso in cui la feature venga eliminata correttamente.
"""

    return delete_feature_context_geometry(uid=uid,cntxt=cntxt,request=request,response=response) 




