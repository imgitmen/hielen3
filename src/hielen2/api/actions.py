#!/usr/bin/env python
# coding=utf-8
import hug
import tempfile
import falcon
import os
import time
import json
from hielen2 import db, conf
from hielen2.utils import hashfile
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from himada.api import ResponseFormatter
from urllib.parse import unquote
from importlib import import_module

@hug.get('/{feature}')
def get_forms(feature,form=None, request=None, response=None):

    out = ResponseFormatter()
      
    # Trying to manage income feature request and its prototype configuration
    try:
        featureobj=db['features'][feature]
        proto=db['features'][feature]['properties']['type']
        protoforms=db['features_proto'][proto]['forms']
    except KeyError as e:
        out.status=falcon.HTTP_NOT_FOUND
        out.message=f"feature '{feature}' does not exists or it is misconfigured: {e}"
        out.format(request=request,response=response)
        return

    if form is not None and form is not list:
        form=[form]

    out.data={}
    for k,w in protoforms.items():
        if form is None or k in form:
            out.data[k]={ y:None for y in w['args'].keys()  }
            try:
                out.data[k].update(featureobj[k])
            except KeyError:
                pass

    out.format(request=request,response=response)
    return


@hug.get('/{feature}/{form}')
def get_form(feature=None,form=None, request=None, response=None):
    return get_forms(feature=feature,form=form,request=request,response=response)


@hug.post('/{feature}/{form}',parse_body=False)
@hug.default_input_format( content_type='multipart/form-data')
def prots(feature=None,form=None, request=None, response=None):
    """
**Esecuzione delle azioni**

Richiede l'esecuzione di una specifica azione su una feature, fornendo tutte le informazioni \
necessarie attraverso una form dinamica dedicata. L'elenco delle azioni possibili per ogni \
feature è disponibile attraverso l'api ... (TODO)

- Oltre ai due parametri `feature` e `form`, indicati nella url, accetta un _multipart/form-data_ \
basato sulla specifica form, selezionata tramite i due parametri espliciti.
- Tutto il content è scaricato attarverso i chunk dello stream ('100 continue') per evitare il \
timeout dei workers in caso di contenuti di grandi dimensioni.

Possibili risposte:

- _404 Not Found_: Nel caso la feature non esista o non sia definita per essa l'azione richiesta.
- _202 Accepted_: Nel caso in cui l'azione vada a buon fine


**TEMPORANEAMENTE**

- E' impementato come _"DUMMY"_: funziona tutto il giro dei check ma i moduli specifici non sono \
ancora agganciati.

- Risponde con un json dict compresivo di tutti campi attesi per la Form selezionata, valorizzati \
in questo modo: 

_Se il campo è stato fornito in input ed è uno scalare, viene fornito il valore di input._

_Se il campo fornito in input è un file, viene fornito il checksum md5 del file, calcolato dopo che \
il file è stato salvato sul filesystem._

_I campi non forniti in input vengono restituiti con valore null._
"""
    out = ResponseFormatter(falcon.HTTP_ACCEPTED)

    # Trying to manage income feature request and its prototype configuration
    try:
        properties=db['features'][feature]['properties']
        proto=properties['type']
        formstruct=db['features_proto'][proto]['forms'][form]

    except KeyError as e:
        out.status=falcon.HTTP_NOT_FOUND
        out.message=f"feature '{feature}' does not exists or it is misconfigured: {e}"
        out.format(request=request,response=response)
        return
    
    parser = StreamingFormDataParser(headers=request.headers)

    values={}

    #TODO Differenziazione delle tipologie di input
    for k,w in formstruct['args'].items():
        if w == 'file':
            timenow=time.perf_counter()
            filepath=os.path.join(tempfile.gettempdir(), f"{feature}{k}{timenow}.part")
            target=FileTarget(filepath)
            parser.register(k, target)
            values[k]=filepath
        else:
            target = ValueTarget()
            parser.register(k, target)
            values[k] = target

    while True:
        chunk = request.stream.read(8192)
        if not chunk:
            break
        parser.data_received(chunk)

    kwargs={}
    for k,w in values.items():
        
        if isinstance(w,str):
#FOR DUMMY RESPONSE
            """
            v=os.path.exists(w) and "md5 "+hashfile(w) or None
            if os.path.exists(w): 
                  os.remove(w)
            """
#REAL
            v=os.path.exists(w) and w or None
        else:
            v=unquote(w.value.decode('utf8')) or None

        kwargs[k]=v

    m = [ m for m in  formstruct['mandatory'] if kwargs[m] is None ]

    if m.__len__():
        out.status=falcon.HTTP_BAD_REQUEST
        out.message=f"Required parameters {m} not supplied"
        out.format(request=request,response=response)
        return

    #CHECKS request checks ALL RIGHT. Continuing with code loading

    # Trying to initialize feature action manager module
    try:
        mod=db['features_proto'][proto]['module']
        mod=import_module(mod)
        source=mod.Source(properties=properties,filecache=conf['filecache'])
        result=eval(f"source.{form}(**kwargs)")

        
#PRODUCTION ERROR MANAGER
    except KeyError as e:
        out.status=falcon.HTTP_NOT_IMPLEMENTED
        out.message=f"Prototype '{proto}' actions not implemented."
        out.format(request=request,response=response)
        return
    except ModuleNotFoundError as e:
        out.status=falcon.HTTP_INTERNAL_SERVER_ERROR
        out.message=f"Prototype '{proto}' module '{mod}' not found."
        out.format(request=request,response=response)
        return  
    except AttributeError as e:
        out.status=falcon.HTTP_NOT_IMPLEMENTED
        out.message=f"Prototype '{proto}' action '{form}' not implemented."
        out.format(request=request,response=response)
        return
    except Exception as e:
        raise e

    try:
        db['features'][feature][form].update(result)
        db['features'].save()
    except KeyError as e:
        out.status=falcon.HTTP_INTERNAL_SERVER_ERROR
        out.message=str(e)
        out.format(request=request,response=response)
        return  


    out.format(request=request,response=response)
    return

