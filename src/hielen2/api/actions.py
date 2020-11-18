#!/usr/bin/env python
# coding=utf-8
import hug
import tempfile
import falcon
import os
import time
import json
from hielen2 import db
from hielen2.utils import hashfile
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from himada.api import ResponseFormatter
from urllib.parse import unquote

@hug.post('/{feature}/{form}',parse_body=False)
@hug.default_input_format( content_type='multipart/form-data')
def prots(feature=None,form=None, request=None, response=None, **kwargs ):
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

- _404 Not Found_: Nel caso la feature non esita o non sia definita per essa l'azione richiesta.
- _202 Accepted_: Nel caso in cui l'azione vada a buon fine


**TEMPORANEAMENTE**

- E' impementato come _"DUMMY"_: funziona tutto il giro dei check ma i moduli specifici non sono \
ancora agganciati.

- Risponde con un json dict compresivo di tutti campi attesi per la Form selezionata, valorizzati \
in questo modo: 

_Se il campo è stato fornito in input ed è uno scalare, viene fornito il valore di input._

_Se il campo fornito in imput è un file, viene fornito il checksum md5 del file, calcolato dopo che \
il file è stato salvato sul filesystem._

_I campi non forniti in input vengono restituiti con valore null._
"""
    out = ResponseFormatter(falcon.HTTP_ACCEPTED)

    try:
        t=db['features'][feature]['type']
        forms=db['features_proto'][t]['forms']
    except KeyError as e:
        out.status=falcon.HTTP_NOT_FOUND
        out.message=f"feature '{feature}' does not exists or it is misconfigured."
        out.format(request=request,response=response)
        return

    try:
        form=forms[form]
    except KeyError as e:
        out.status=falcon.HTTP_NOT_FOUND
        out.message=f"No '{form}' form defined for feature '{feature}'"
        out.format(request=request,response=response)
        return


    mandatory=form['mandatory'].keys()

    expected_fields={ **form['mandatory'], **form['optional'] }

    parser = StreamingFormDataParser(headers=request.headers)

    values={}

    for k,w in expected_fields.items():
        if w == 'file':
            t=time.perf_counter()
            filepath=os.path.join(tempfile.gettempdir(), f"{feature}{k}{t}.part")
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
            v=os.path.exists(w) and "md5 "+hashfile(w) or None
            if os.path.exists(w): 
                  os.remove(w)
#REAL
#            v=os.path.exists(w) and hashfile(w) or None
        else:
            v=unquote(w.value.decode('utf8')) or None

        kwargs[k]=v


    m = [ m for m in mandatory if kwargs[m] is None ]

    if m.__len__():
        out.status=falcon.HTTP_BAD_REQUEST
        out.message=f"Required parameters {m} not supplied"
        out.format(request=request,response=response)
        return

    return kwargs

