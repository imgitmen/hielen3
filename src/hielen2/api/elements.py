#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen2 import db
from himada.api import ResponseFormatter


@hug.post('/')
def create_elements(code,prototype,geom=None,request=None,response=None):

    '''
**Api di creazione degli elementi.**

Ogni elemento deve avere il suo codice univoco `code` e il suo prototipo `prototype`. Il prototipo \
dell'elemento forisce informazioni per l'inizializazione della struttura.

Possibili risposte:

- _409 Conflict_: Nel caso in cui il codice fornito esista già.
- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _201 Created_: Nel caso in cui l'elemento venga creato correttamente.
'''

    out = ResponseFormatter(status=falcon.HTTP_CREATED)
    try:
        proto= db['elements_proto'][prototype]['struct']
        proto['parameters']={ k:None for k in proto['parameters'].keys()}
        db['elements'][code]=proto
        out.message=proto
    except KeyError as e:
        out.message=f"prototype '{prototype}' not found."
        out.status=falcon.HTTP_NOT_FOUND
    except ValueError as e:
        out.message=f"element '{code}' exists"
        out.status=falcon.HTTP_CONFLICT

    response=out.format(response=response,request=request)
    return



def elinfo(el):

    if el is None:
       return None
     
    info={ k:w for k,w in el.items() if k not in ('code',) }

    info['parameters']=[ 
            {
                'series':e[1],
                'name':e[0], 
                'unit': db['series'][e[1]]['mu']
            } for e in el['parameters'].items() if e[1] is not None ]
     
    return info  


@hug.get('/',examples='')
def elements_info( elist=None, request=None, response=None ):

    out = ResponseFormatter()
    out.data={ k:elinfo(w) for k,w in db['elements'][elist].items() }
    response = out.format(response=response,request=request)

    return


@hug.get('/{code}')
def element_info( code, request=None, response=None ):

    out = ResponseFormatter()

    try: 
        out.data= db['elements'][code]
    except KeyError as e:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
        out.message=f"element '{code}' not found"

    response = out.format(response=response,request=request)
    return

@hug.delete('/{code}')
def element_delete(code, request=None, response=None):
    
    out = ResponseFormatter()

    try:
        out.data = db['elements'].pop(code)
    except KeyError as e:
        out = ResponseFormatter(status=falcon.HTTP_NOT_FOUND)
        out.message=f"element '{code}' not found"
        
    response = out.format(response=response,request=request)
    return



