#!/usr/bin/env python
# coding=utf-8
import hug
import tempfile
import falcon
import os
import time
import json
from hielen2 import db, conf
import hielen2.source as sourceman
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from himada.api import ResponseFormatter
from urllib.parse import unquote
from importlib import import_module


@hug.get("/{feature}")
def features_actions_values(feature, actions=None, timestamp=None, request=None, response=None):

    """
**Recupero dello stato corrente delle azioni effettuate su una feature**

L'intento di questa api è quello di fornire i valori richiesti secondo lo schema dell'azione  
 
___nota 1___: `actions` accetta valori multipli separati da virgola
___nota 2___: A seconda dell'action richiesta, alcuni parametri potrebbero essere utilizzati in fase \
di input ma non registrati. Il che vuol dire che per quei parametri il valore di ritorno sarà null
 
viene restituito una struttura di questo tipo:

        [
            { "feature"*:...,
              "action_name*":...,
              "timestamp": ...,
              "value":{...}
            },
            { "feature"*:...,
              "action_name*":...,
              "timestamp": ...,
              "value":{...}
            },
            ...
        ]


___nota 3___ :(*) I campi "feature" e "action" potrebbero non essere restituiti nella struttura \
nel caso in cui essi risultino non ambigui. "timestamp" e "value" vengono sempre restituiti

Possibili risposte:
 
- _404 Not Found_: Nel non venga trovata la feature richiesta o essa abbia un problema di \
configurazione

"""
    out = ResponseFormatter()

    # Trying to manage income feature request and its prototype configuration
    try:
        feat = db["features"][feature]
        featobj = sourceman.sourceFactory(feat,conf['filecache'])
        out.data = featobj.getActionValues(actions,timestamp)
        if not isinstance(out.data,list):
            out.data=[out.data]
    except Exception as e:
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{feature}' does not exists or it is misconfigured: {e}"
        out.format(request=request, response=response)
        return

    out.format(request=request, response=response)
    return

@hug.get("/{feature}/{action}")
def feature_action_values(feature, action, timestamp=None, request=None, response=None):
    """
    **Recupero dello stato corrente per una specifica azione di una specifica feature**"""
    return features_actions_values(feature, action, timestamp, request=request, response=response)


@hug.delete("/{feature}/{action}")
def feature_action_delete(feature,action,timestamp,request=None,response=None):
    """
    **Eliminazione di una determinata azione di una secifica feature**"""
    out = ResponseFormatter()

    # Trying to manage income feature request and its prototype configuration
    try:
        feat = db["features"][feature]
        featobj = sourceman.sourceFactory(feat,conf['filecache'])
        out.data = featobj.deleteActionValues(action,timestamp)
    except Exception as e:
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{feature}' does not exists or it is misconfigured: {e}"
        out.format(request=request, response=response)
        return

    out.format(request=request, response=response)
    return



@hug.post("/{feature}/{action}", parse_body=False)
@hug.default_input_format(content_type="multipart/form-data")
def make_action(feature, action, request=None, response=None):
    """
**Esecuzione delle azioni**

Richiede l'esecuzione di una specifica azione su una feature, fornendo tutte le informazioni \
necessarie attraverso una form dinamica dedicata.

- Oltre ai due parametri `feature` e `form`, `timestamp`, indicati nella url, accetta un \
_multipart/form-data_ basato sulla specifica form, selezionata tramite i due parametri espliciti.
- Tutto il content è scaricato attarverso i chunk dello stream ('100 continue') per evitare il \
timeout dei workers in caso di contenuti di grandi dimensioni.

Possibili risposte:

- _200 OK_: Nel caso in cui l'azione vada a buon fine. L'azione richiesta viene presa in carico ma \
potrebbe avere un tempo di esecuzione arbitrario. L'azione quindi viene splittata su un altro processo.
- _404 Not Found_: Nel caso la feature non esista o non sia definita per essa l'azione richiesta.
- _500 Internal Server Error_: Nel caso pessimo che il modulo dichiarato non esista.
- _501 Not Implemented'_: Nel caso la tipologia non fornisse ancora l'iplementazione di uno o tutti \
i moduli di gestione


E' stato implementato il meccanismo minimo di gestione che prevede il salvataggio delle info \
fornite che possono essere fornite tali e quali in uscita (vedi metodo GET dell'api). Questo \
meccanismo permette di svluppare i moduli a partire da un template con risposta di default.

"""
    out = ResponseFormatter()

    # Trying to manage income feature request and its prototype configuration
    try:
        feat = db["features"][feature]
        featobj = sourceman.sourceFactory(feat,conf['filecache'])
    except KeyError as e:
        #raise e
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{feature}' does not exists or it is misconfigured: {e}"
        out.format(request=request, response=response)
        return
    
    try:
        schema=featobj.getActionSchema(action)
    except KeyError as e:
        raise e
        out.status = falcon.HTTP_NOT_IMPLEMENTED
        out.message = f"Prototype '{featobj.type}' actions not implemented."
        out.format(request=request, response=response)
        return
    except ModuleNotFoundError as e:
        #raise e
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR
        out.message = f"Prototype '{featobj.type}' module not found."
        out.format(request=request, response=response)
        return

    parser = StreamingFormDataParser(headers=request.headers)

    values = {}

    # TODO Differenziazione delle tipologie di input
    for k, w in schema["fields"].items():
        if w == "LocalFile":
            timenow = time.perf_counter()
            filepath = os.path.join(
                tempfile.gettempdir(), f"{feature}.{k}.{timenow}.part"
            )
            target = FileTarget(filepath)
            parser.register(k, target)
            values[k] = filepath
        else:
            target = ValueTarget()
            parser.register(k, target)
            values[k] = target

    while True:
        chunk = request.stream.read(8192)
        if not chunk:
            break
        parser.data_received(chunk)

    kwargs = {}

    for k, w in values.items():
        if isinstance(w, str):
            v = os.path.exists(w) and w or None
        else:
            v = unquote(w.value.decode("utf8")) or None
        kwargs[k] = v

    m = [m for m in schema["required"] if kwargs[m] is None]

    if m.__len__():
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"Required parameters {m} not supplied"
        out.format(request=request, response=response)
        return

    # CHECKS request checks ALL RIGHT. Continuing with code loading

    # Trying to initialize feature action manager module
    try:
        result = featobj.execAction(action,**kwargs)
    except AttributeError as e:
        out.status = falcon.HTTP_NOT_IMPLEMENTED
        out.message = f"Action '{action}' not implemented."
        out.format(request=request, response=response)
        return
    except ValueError as e:
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"Action values error: {e}."
        out.format(request=request, response=response)
        return

    except Exception as e:
        raise e
        pass

    try:
        db["actions"][feature,action,result['timestamp']]={"value":result}
        db["features"].save()
    except KeyError as e:
        #raise e
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR
        out.message = str(e)
        out.format(request=request, response=response)
    except ValueError as e:
        #raise e
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = str(e)
        out.format(request=request, response=response)

        return

    out.format(request=request, response=response)
    return
