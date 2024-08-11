#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
import json
from hielen3 import db
from hielen3.utils import JsonValidable, hasher, ResponseFormatter, uuid, dataframe2jsonizabledict
from hielen3.feature import HFeature,HSeries
from pandas import Series
from marshmallow import Schema, fields
import traceback


class ThresholdSchema(Schema):
    label = fields.Str(required=True)
    ttype = fields.Str(required=True)
    value = fields.Number(required=True)
    color = fields.Str(required=False)
    recipients = fields.Str(required=False)


# GET


@hug.get("/")
def retrive_thresholds(
    series=None,
    labels=None,
    ttype=None,
    request=None,
    response=None,
    **kwargs
):
    """
DESCRIZIONE:

**Interrogazione valori di Soglia associati alle serie dati.**

la struttura logica di associazione delle soglie segue questo schema gerarchico:

    series -n--n-> label -1--enum-> ttype

    dove
    - _series_ è una serie dati specifica.
    - _label_ è un'etichetta arbitraria, che a livello applicativo identifica
      la soglia (es.: 'Alert', 'Alarm' etc.).
    - _ttype_ è un enum ('UPPER','LOWER','BAND') che definisce rispettivamente
     se la soglia è un limite superiore, inferiore o simmetricamente, entrambi

la tupla (series,label,ttype) identifica la chiave univoca della soglia

a questa tupla vengono associate queste informazioni:

    - _value_ il valore numerico della soglia
    - _color_ il colore da assegnare alla soglia (Hex), info per livello 
      applicativo
    - _recipients_ lista csv di contatti associati alla soglia, 
      info per livello applicativo 


PARAMETRI:

- **series**: array di uuid delle serie per cui recuperare le info 

- **labels**: array di labels per cui recuperare le info:

- **ttype**: array di valori ttype validi


OUTPUT:

Se vengono trovate lifo corrispondenti ai criteri di interrogazione, viene restituito
all'interno del campo `data` del json di risposta standard una struttura con questo formato:

        [
            {
                "series":"...",
                "label":"...",
                "ttype":"...",
                "value":...,
                "color":...,
                "recipients:"..."
            },
            ...
        ]

RESPONSE CODES:

- _404 Not Found_: Nel caso in cui l'interrogazione non produca risultati.
- _200 OK_: Nel caso in cui l'interrogazione vada a buon fine.

"""
    out = ResponseFormatter(status=falcon.HTTP_OK)

    if isinstance(series,str): series=series.split(",")
    
    if not isinstance(series,(list,set,tuple)) and series is not None:
        series=[series]

    if not series is None: series = [ a for a in series if a is not None and a.__len__()]
    if not series is None and not series.__len__(): series = None
     
    if isinstance(labels,str): labels=labels.split(",")

    if not isinstance(labels,(list,set,tuple)) and labels is not None:
        labels=[labels]

    if not labels is None: labels = [ a for a in labels if a is not None and a.__len__()]
    if not labels is None and not labels.__len__(): labels = None

    if isinstance(ttype,str): ttype=ttype.split(",")
                                                                                                                                                                             
    if not isinstance(ttype,(list,set,tuple)) and ttype is not None:
        ttype=[ttype]
               
    if not ttype is None: ttype = [ a for a in ttype if a is not None and a.__len__()]
    if not ttype is None and not ttype.__len__(): ttype = None


    #DEBUG print ({"series":series,"labels":labels})

    try:
        out.data=db['series_thresholds'][{"series":series,"label":labels,"ttype":ttype}].to_dict(orient="records")
    except KeyError as e:
        out.message = e.args
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = e.args
        out.status = falcon.HTTP_CONFLICT
        pass
 

    response = out.format(response=response, request=request)
     
    return  

@hug.get("/{series}")
def retive_s_thresholds(
    series,
    labels=None,
    ttype=None,
    request=None,
    response=None,
    **kwargs
):
    """
DESCRIZIONE:

**ALIAS di GET /thresholds**

"""


    return retrive_thresholds(series,labels,ttype,request,response,**kwargs)


@hug.get("/{series}/{labels}")
def retive_s_l_thresholds(
    series,
    labels,
    ttype=None,
    request=None,
    response=None,
    **kwargs
):
    """
DESCRIZIONE:

**ALIAS di GET /thresholds**

"""

    return retrive_thresholds(series,labels,ttype,request,response,**kwargs)

@hug.get("/{series}/{labels}/{ttype}")
def retive_s_l_t_thresholds2(
    series,
    labels,
    ttype,
    request=None,
    response=None,
    **kwargs
):
    """
DESCRIZIONE:

**ALIAS di GET /thresholds**

"""

    return retrive_thresholds(series,labels,ttype,request,response,**kwargs)


# POST

@hug.post("/")
def create_thresholds(
    series,
    thresholds: JsonValidable(ThresholdSchema(many=True)),
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

**Modifica delle soglie. utilizza una struttura json in ingresso**

PARAMETRI:

- **series**: array di uuid delle serie per cui modificare le soglie 

- **thresholds**: Json dei campi delle soglie. Lo schema è il seguente:


        {
            "label": "Stringa: tipologia di soglia ('Alarm','Alert',...)",
            "ttype":  "Stringa: tipo: Superiore ( 'UPPER' ), inferiore ( 'LOWER' )",
            "value": "Numero: valore della soglia,
            "color": "Stringa: colore della soglia",
            "recipients": "Stringa: 'intesa come elenco di email'"
        }


OUTPUT:

Se la soglia viene creata/modificata correttamente la sua struttura viene restituita all'interno del campo \
`data` del json di risposta standard

RESPONSE CODES:

- _404 Not Found_: Nel caso in cui le serie richieste non esistano.
- _200 OK_: Nel caso in cui la feature venga creata correttamente.
"""
    out = ResponseFormatter(status=falcon.HTTP_OK)

    if isinstance(series,str): series=series.split(",")
    
    if not isinstance(series,(list,set,tuple)) and series is not None:
        series=[series]

    if not series is None: series = [ a for a in series if a is not None and a.__len__()]
    if not series is None and not series.__len__(): series = None
 
    try:
        for s in series:
            HSeries(db['series'][s]['uuid'].squeeze()).attribute_update(attribute="thresholds",value=thresholds)
    except KeyError as e:
        out.message = f"series '{s}' not found."
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = e.args
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return

@hug.post("/{series}")
def create_s_thresholds(
    series,
    thresholds: JsonValidable(ThresholdSchema(many=True)),
    request=None,
    response=None,
    **kwargs
):
    """
DESCRIZIONE:

**ALIAS di POST /thresholds**

"""

    return create_thresholds(series,thresholds,request,response,**kwargs)

@hug.post("/{series}/{labels}")
def create_s_l_thresholds(
    series,
    labels,
    ttype,
    value,
    color=None,
    recipients=None,
    request=None,
    response=None,
    **kwargs
):
    """
DESCRIZIONE:

**Modifica delle soglie. Utilizza variabili esplicite in input**

PARAMETRI:

- **series**: array di uuid delle serie per cui modificare le soglie 

- **label**: tipologia di soglia ('Alarm','Alert',...)
- **ttype**: tipo: Superiore ( 'UPPER' ), inferiore ( 'LOWER' )
- **value**: valore della soglia
- **color**: colore della soglia
- **recipients**: stringa csv intesa come elenco di contatti

OUTPUT:

Se la soglia viene creata/modificata correttamente la sua struttura viene restituita all'interno del campo \
`data` del json di risposta standard

RESPONSE CODES:

- _404 Not Found_: Nel caso in cui le serie richieste non esistano.
- _200 OK_: Nel caso in cui la feature venga creata correttamente.
"""

    if isinstance(labels,str): labels=labels.split(",")

    if not isinstance(labels,(list,set,tuple)) and labels is not None:
        labels=[labels]

    if not labels is None: labels = [ a for a in labels if a is not None and a.__len__()]
    

    if isinstance(ttype,str): ttype=ttype.split(",")

    if not isinstance(ttype,(list,set,tuple)) and ttype is not None:
        ttype=[ttype]
               
    if not ttype is None: ttype = [ a for a in ttype if a is not None and a.__len__()]

    infos={"value":value}

    if color is not None: infos["color"] = color
    if recipients is not None: infos["recipients"] = recipients

    thresholds=[]

    for l in labels:
        for t in ttype:
            thresholds.append(dict(label=l,ttype=t,**infos))

    thresholds = ThresholdSchema(many=True).loads(json.dumps(thresholds))

    return create_thresholds(series,thresholds,request,response,**kwargs)


@hug.post("/{series}/{labels}/{ttype}")
def create_s_l_t_thresholds(
    series,
    labels,
    ttype,
    value,
    color=None,
    recipients=None,
    request=None,
    response=None,
    **kwargs
):
    """
DESCRIZIONE:

**ALIAS di POST /thresholds/{labels}**

"""


    return create_s_l_thresholds(series,labels,ttype,value,color,recipients,request,response)


# DELETE

@hug.delete("/")                                         
def delete_thresholds(                                            
    series,                                                            
    labels=None,                                                            
    ttype=None,
    request=None,                                                      
    response=None,
    **kwargs                                                           
): 
    """
DESCRIZIONE:

**Eliminazione delle soglie. Utilizza variabili esplicite in input**

PARAMETRI:

- **series**: array di uuid delle serie per cui modificare le soglie 
- **label**: array tipologie di soglia ('Alarm','Alert',...)
- **ttype**: array di valori dell'enum Superiore ( 'UPPER' ), inferiore ( 'LOWER' )

OUTPUT:

Se le soglie selezionate vengono eleiminate correttamente la loro struttura viene restituita
all'interno del campo `data` del json di risposta standard

RESPONSE CODES:

- _404 Not Found_: Nel caso in cui le serie richieste non esistano.
- _200 OK_: Nel caso in cui la feature venga creata correttamente.
"""



    out = ResponseFormatter(status=falcon.HTTP_OK)

    if isinstance(series,str): series=series.split(",")
    
    if not isinstance(series,(list,set,tuple)) and series is not None:
        series=[series]

    if not series is None: series = [ a for a in series if a is not None and a.__len__()]
    if not series is None and not series.__len__(): series = None
     
    if isinstance(labels,str): labels=labels.split(",")

    if not isinstance(labels,(list,set,tuple)) and labels is not None:
        labels=[labels]

    if not labels is None: labels = [ a for a in labels if a is not None and a.__len__()]
    if not labels is None and not labels.__len__(): labels = None

    if isinstance(ttype,str): ttype=ttype.split(",")
                                                                                                                                                                             
    if not isinstance(ttype,(list,set,tuple)) and ttype is not None:
        ttype=[ttype]
               
    if not ttype is None: ttype = [ a for a in ttype if a is not None and a.__len__()]
    if not ttype is None and not ttype.__len__(): ttype = None


    #DEBUG print ({"series":series,"labels":labels})

    try:
        if series is None: raise Exception("series not provided") 
        out.data=db['series_thresholds'].pop({"series":series,"label":labels}).to_dict(orient="records")
    except KeyError as e:
        out.message = e.args
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = e.args
        out.status = falcon.HTTP_CONFLICT
        pass
 

    response = out.format(response=response, request=request)
     
    return  

@hug.delete("/{series}")
def delete_s_thresholds(
    series,      
    labels=None,
    ttype=None,
    request=None,
    response=None,
    **kwargs
):
    """
DESCRIZIONE:

**ALIAS di DELETE /thresholds**

"""

    return delete_thresholds(series,labels,ttype,request,response,**kwargs)
                 
 
@hug.delete("/{series}/{labels}")
def delete_s_l_thresholds(
    series,
    labels,
    ttype=None,
    request=None,
    response=None,
    **kwargs
):
    """
DESCRIZIONE:

**ALIAS di DELETE /thresholds**

"""

    return delete_thresholds(series,labels,ttype,request,response,**kwargs)

@hug.delete("/{series}/{labels}/{ttype}")
def delete_s_l_t_thresholds(
    series,
    labels,
    ttype,
    request=None,
    response=None,
    **kwargs
):
    """
DESCRIZIONE:

**ALIAS di DELETE /thresholds**

"""

    return delete_thresholds(series,labels,ttype,request,response,**kwargs)
