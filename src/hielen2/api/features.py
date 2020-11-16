#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen2 import db
from hielen2.utils import JsonValidable
from marshmallow import Schema, fields
from himada.api import ResponseFormatter
from marshmallow_geojson import GeoJSONSchema


class FeatureSchema(Schema):
    uid=fields.Str(required=True,allow_none=False)
    prototype=fields.Str(required=True,allow_none=False)
    context=fields.Str(default="decontextualized",allow_none=False)
    label=fields.Str(default=None)
    description=fields.Str(default=None)
    style=fields.Str(default=None)
    status=fields.Str(default=None)
    geometry=fields.Nested(GeoJSONSchema)


@hug.post('/')
def create_feature(feature:JsonValidable(FeatureSchema()),request=None,response=None):

    '''
**Creazione delle Features.**

Ogni feature deve avere il suo codice univoco `uid` e il suo prototipo `prototype`.
Il prototipo della feature forisce informazioni per l'inizializazione della struttura.
Il parametro geometry deve essere un GeoJson (ancora non validato)

Se la feature viene creata correttamente ne restituisce la struttura

Possibili risposte:

- _409 Conflict_: Nel caso in cui il uid fornito esista già.
- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _201 Created_: Nel caso in cui la feature venga creata correttamente.
'''

    

    out = ResponseFormatter(status=falcon.HTTP_CREATED)
    try:
        prototype=feature.pop('prototype')
        try:
            if feature['context'] is None:
                feature['context']='decontextualized'
        except KeyError:
            feature['context']='decontextualized'

        feature.update( db['features_proto'][prototype]['struct'] )
        feature['parameters']={ k:None for k in feature['parameters'].keys()}
        db['features'][feature['uid']]=feature
        out.message=db['features'][feature['uid']]
    except KeyError as e:
        out.message=f"prototype '{prototype}' not found."
        out.status=falcon.HTTP_NOT_FOUND
    except ValueError as e:
        out.message=f"feature '{feature['uid']}' exists"
        out.status=falcon.HTTP_CONFLICT

    response=out.format(response=response,request=request)
    return

@hug.get('/')
def features_info( uids=None, cntxt=None, request=None, response=None ):
    '''
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
	}

___nota___: Al contrario di quanto detto nel TODO non viene inserito il context a livello \
"features" perchè in effetti è una informazione sempre conosciuta a priori (se si lavora \
per commesse). Al contrario se si lavora per uids allora ha senso inserie questa info all' \
interno delle properties delle singole features.


Possibili risposte:

- _404 Not Found_: Nel caso in cui nessuna feature risponda ai criteri

'''


    def _format(ft):
        try:
            return { "type":"Feature", "properties":{ k:w for k,w in ft.items() if not k == "parameters" } }
        except Exception as e:
            raise e

    out = ResponseFormatter()

    if not isinstance(uids,(list,set)) and uids is not None:
        uids=[uids]

    try:
        out.data=dict( 
            features=[ _format(v) for v in db['features'][uids].values() 
                if cntxt is None or v['context']==cntxt ] 
            )
    except KeyError as e:
        out.status=falcon.HTTP_NOT_FOUND
        out.message=(str(e))

    response = out.format(response=response,request=request)
    return



@hug.get('/{uid}')
def feature_info( uid, cntxt=None, request=None, response=None ):
    """
**Alias di recupero informazioni della specifica feature**

"""
    return features_info(uid,cntxt,request,response)



##@hug.delete('/{cntxt}/{uid}')
##def del_feature( cntxt,uid, request=None, response=None ):
@hug.delete('/{uid}')
def del_feature( uid, request=None, response=None ):

    """
**Cancellazione delle Features**

Se la feature viene cancellata correttamente ne restituisce la struttura

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _200 OK_: Nel caso in cui la feature venga creata correttamente.

"""

    out = ResponseFormatter()
    
    if uid is None:
        out.status=falcon.HTTP_BAD_REQUEST
        out.message="None value not allowed"

    try:
        out.data=db['features'][uid]
        db['features'][uid]=None
    except KeyError as e:
        out.status=falcon.HTTP_NOT_FOUND
        out.message=f"feature '{uid}' not foud."

    response = out.format(response=response,request=request)
    return

