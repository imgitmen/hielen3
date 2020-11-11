#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen2 import db
from hielen2.utils import JsonValidable
from marshmallow import Schema, fields
from himada.api import ResponseFormatter



class ElementSchema(Schema):
    uuid=fields.Str(required=True,allow_none=False)
    prototype=fields.Str(required=True,allow_none=False)
    context=fields.Str(default=None)
    label=fields.Str(default=None)
    description=fields.Str(default=None)
    style=fields.Str(default=None)
    status=fields.Str(default=None)
    geom=fields.Str(default=None)


@hug.post('/')
#def create_elements(uuid,prototype,label=None,descritpion=None,context=None,geom=None,request=None,response=None)
def create_elements(el:JsonValidable(ElementSchema()),request=None,response=None):

    '''
**Api di creazione degli elementi.**

Ogni elemento deve avere il suo codice univoco `uuid` e il suo prototipo `prototype`. Il prototipo \
dell'elemento forisce informazioni per l'inizializazione della struttura.

Possibili risposte:

- _409 Conflict_: Nel caso in cui il codice fornito esista già.
- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _201 Created_: Nel caso in cui l'elemento venga creato correttamente.
'''

    

    out = ResponseFormatter(status=falcon.HTTP_CREATED)
    try:
        prototype=el.pop('prototype')
        el.update( db['elements_proto'][prototype]['struct'] )
        el['parameters']={ k:None for k in el['parameters'].keys()}
        db['elements'][el['uuid']]=el
        out.message=el
    except KeyError as e:
        out.message=f"prototype '{prototype}' not found."
        out.status=falcon.HTTP_NOT_FOUND
    except ValueError as e:
        out.message=f"element '{el['uuid']}' exists"
        out.status=falcon.HTTP_CONFLICT

    response=out.format(response=response,request=request)
    return



def elinfo(el):

    if el is None:
       return None
     
    info={ k:w for k,w in el.items() if k not in ('uuid',) }

    info['parameters'] = []

    try:
        for e in el['parameters'].items():
            if e[1] is not None:
                info['parameters'].append(
                        {
                            'series':e[1],
                            'name':e[0],
                            'unit': db['series'][e[1]]['mu']
                        }
                )
    except AttributeError:
        pass

    return info  


@hug.get('/',examples='')
def elements_info( elist=None, context=None, request=None, response=None ):

    out = ResponseFormatter()
    out.data={ k:elinfo(w) for k,w in db['elements'][elist].items() if context is None or w['context']==context }
    response = out.format(response=response,request=request)

    return


@hug.get('/{uuid}')
def element_info( uuid, request=None, response=None ):
    out = ResponseFormatter()

    try: 
        out.data= db['elements'][uuid]
    except KeyError as e:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
        out.message=f"element '{uuid}' not found"

    response = out.format(response=response,request=request)
    return 


@hug.delete('/{uuid}')
def element_delete(uuid, request=None, response=None):
    
    out = ResponseFormatter()

    try:
        out.data = db['elements'].pop(uuid)
    except KeyError as e:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
        out.message=f"element '{uuid}' not found"
        
    response = out.format(response=response,request=request)
    return



