#!/usr/bin/env python
# coding=utf-8
import hug
import tempfile
import falcon
import os
import time
import json
from hielen3 import db, conf
from hielen3.feature import HFeature
from hielen3.utils import ResponseFormatter
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from urllib.parse import unquote
from importlib import import_module
from pathlib import Path, PosixPath

import traceback

'''
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
        featobj = sourceman.sourceFactory(feature)
        out.data = featobj.getActionValues(actions,timestamp)
        if not isinstance(out.data,list):
            out.data=[out.data]
    except Exception as e:
        traceback.print_exc()
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
    **Eliminazione di una determinata azione di una specifica feature**"""
    out = ResponseFormatter()

    # Trying to manage income feature request and its prototype configuration
    try:
        featobj = sourceman.sourceFactory(feature)
        out.data = featobj.deleteActionValues(action,timestamp)
    except Exception as e:
        traceback.print_exc()
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{feature}' does not exists or it is misconfigured: {e}"
        out.format(request=request, response=response)
        return

    out.format(request=request, response=response)
    return
'''


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
        featobj = HFeature.retrive(feature)
    except KeyError as e:
        traceback.print_exc()
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{feature}' does not exists or it is misconfigured: {e}"
        out.format(request=request, response=response)
        return
    
    try:
        schema=featobj.schemata[action]
    except KeyError as e:
        raise e
        traceback.print_exc()
        out.status = falcon.HTTP_NOT_IMPLEMENTED
        out.message = f"Prototype '{featobj.ftype}' actions not implemented."
        out.format(request=request, response=response)
        return
    except ModuleNotFoundError as e:
        traceback.print_exc()
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR
        out.message = f"Prototype '{featobj.ftype}' module not found."
        out.format(request=request, response=response)
        return

    parser = StreamingFormDataParser(headers=request.headers)

    values = {}
    toremove = []

    # TODO Differenziazione delle tipologie di input
    for k, w in schema["fields"].items():
        if w == "LocalFile":
            timenow = time.perf_counter()
            filepath = Path(
                tempfile.gettempdir(), f"{feature}.{k}.{timenow}.part"
            )
            target = FileTarget(filepath)
            parser.register(k, target)
            values[k] = filepath
            toremove.append(filepath)
        else:
            target = ValueTarget()
            parser.register(k, target)
            values[k] = target

    def removetempfiles(toremove):
        for v in toremove:
            try:
                os.unlink(v)
            except FileNotFoundError as e:
                pass

    while True:
        chunk = request.stream.read(8192)
        if not chunk:
            break
        parser.data_received(chunk)

    kwargs = {}

    for k, w in values.items():
        model = schema["fields"][k]

        if model == "LocalFile":
            #v = os.path.exists(w) and str(w) or None
            v = str(w)
        elif model == "FTPPath":
            v = unquote(w.value.decode("utf8")) or None
            if v is not None:
                v=Path(v)
        else:
            v = unquote(w.value.decode("utf8")) or None
        kwargs[k] = v

    m = [m for m in schema["required"] if kwargs[m] is None]

    if m.__len__():
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"Required parameters {m} not supplied"
        out.format(request=request, response=response)
        removetempfiles(toremove)
        return

    # CHECKS request checks ALL RIGHT. Continuing with code loading

    # Trying to initialize feature action manager module
    try:
        result = featobj.execute(action,**kwargs)
    except AttributeError as e:
        raise e
        traceback.print_exc()
        out.status = falcon.HTTP_NOT_IMPLEMENTED
        out.message = f"Action '{action}' not implemented."
        out.format(request=request, response=response)
        removetempfiles(toremove)
        return

    except Exception as e:
        traceback.print_exc()
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"Action values error: {e}."
        out.format(request=request, response=response)
        removetempfiles(toremove)
        return

    out.format(request=request, response=response)
    removetempfiles(toremove)
    return

@hug.put("/{feature}/{action}", parse_body=False)
@hug.default_input_format(content_type="multipart/form-data")
def update_action(feature, action, request=None, response=None):
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
        featobj = sourceman.sourceFactory(feature)
    except KeyError as e:
        traceback.print_exc()
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature '{feature}' does not exists or it is misconfigured: {e}"
        out.format(request=request, response=response)
        return
    
    try:
        schema=featobj.getActionSchema(action)
    except KeyError as e:
        traceback.print_exc()
        out.status = falcon.HTTP_NOT_IMPLEMENTED
        out.message = f"Prototype '{featobj.type}' actions not implemented."
        out.format(request=request, response=response)
        return
    except ModuleNotFoundError as e:
        traceback.print_exc()
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR
        out.message = f"Prototype '{featobj.type}' module not found."
        out.format(request=request, response=response)
        return

    parser = StreamingFormDataParser(headers=request.headers)

    values = {}
    toremove = []

    # TODO Differenziazione delle tipologie di input
    for k, w in schema["fields"].items():
        if w == "LocalFile":
            timenow = time.perf_counter()
            filepath = Path(
                tempfile.gettempdir(), f"{feature}.{k}.{timenow}.part"
            )
            target = FileTarget(filepath)
            parser.register(k, target)
            values[k] = filepath
            toremove.append(filepath)
        else:
            target = ValueTarget()
            parser.register(k, target)
            values[k] = target

    def removetempfiles(toremove):
        for v in toremove:
            try:
                os.unlink(v)
            except FileNotFoundError as e:
                pass

    while True:
        chunk = request.stream.read(8192)
        if not chunk:
            break
        parser.data_received(chunk)

    kwargs = {}

    for k, w in values.items():
        model = schema["fields"][k]

        if model == "LocalFile":
            #v = os.path.exists(w) and str(w) or None
            v = str(w)
        elif model == "FTPPath":
            v = unquote(w.value.decode("utf8")) or None
            if v is not None:
                v=str(Path(conf['ftproot'],v))
        else:
            v = unquote(w.value.decode("utf8")) or None
        kwargs[k] = v

    # CHECKS request checks ALL RIGHT. Continuing with code loading

    # Trying to initialize feature action manager module
    try:
        result = featobj.updateAction(action,**kwargs)
    except AttributeError as e:
        traceback.print_exc()
        out.status = falcon.HTTP_NOT_IMPLEMENTED
        out.message = f"Action '{action}' not implemented."
        out.format(request=request, response=response)
        removetempfiles(toremove)
        return

    except Exception as e:
        traceback.print_exc()
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = f"Action values error: {e}."
        out.format(request=request, response=response)
        removetempfiles(toremove)
        return

    try:
        db["actions"][feature,action,result['timestamp']]=None
    except Exception:
        pass

    try:
        db["actions"][feature,action,result['timestamp']]={"value":result}
        out.format(request=request, response=response)
    except KeyError as e:
        traceback.print_exc()
        out.status = falcon.HTTP_INTERNAL_SERVER_ERROR
        out.message = str(e)
        out.format(request=request, response=response)
    except ValueError as e:
        traceback.print_exc()
        out.status = falcon.HTTP_BAD_REQUEST
        out.message = str(e)
        out.format(request=request, response=response)

    removetempfiles(toremove)
    return
