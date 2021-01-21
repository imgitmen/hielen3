#Features
## **/features/**

#### POST
-------------
_params_:

- **uid**: Basic text / string value
- **prototype**: Basic text / string value
- **properties**: JSON Schema {**style**: str|bytes, **description**: str|bytes, **status**: str|bytes, **context**: str|bytes, **location**: str|bytes, **label**: str|bytes, **timestamp**: str|bytes}
- **geometry**: JSON Schema {}

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Creazione delle Features.**

Ogni feature deve avere il suo codice univoco `uid` e il suo prototipo `prototype`. Questi due campi sono immutabli (vedi PUT `/feature/{uid}`).
Il prototipo della feature forisce informazioni per l'inizializazione della struttura.
Il parametro `geometry` deve essere un GeoJson

Se la feature viene creata correttamente ne restituisce la struttura

Possibili risposte:

- _409 Conflict_: Nel caso in cui il uid fornito esista già.
- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _201 Created_: Nel caso in cui la feature venga creata correttamente.






#### GET
-------------
_params_:

- **uids**: Basic text / string value
- **cntxt**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


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
            ]
        }


___nota___: Al contrario di quanto detto nel TODO non viene inserito il context a livello "features" perchè in effetti è una informazione sempre conosciuta a priori (se si lavora per commesse). Al contrario se si lavora per uids allora ha senso inserie questa info all' interno delle properties delle singole features.


Possibili risposte:

- _404 Not Found_: Nel caso in cui nessuna feature risponda ai criteri







## **/features/{uid}**

#### GET
-------------
_params_:

- **uid**: Basic text / string value
- **cntxt**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


    **Alias di recupero informazioni della specifica feature**





#### PUT
-------------
_params_:

- **uid**: Basic text / string value
- **properties**: JSON Schema {**style**: str|bytes, **description**: str|bytes, **status**: str|bytes, **context**: str|bytes, **location**: str|bytes, **label**: str|bytes, **timestamp**: str|bytes}
- **geometry**: JSON Schema {}

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Modifica delle properties di una feature**

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _202 Accepted_: Nel caso in cui la feature venga modificata correttamente.






#### DELETE
-------------
_params_:

- **uid**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Cancellazione delle Features**

Se la feature viene cancellata correttamente ne restituisce la struttura

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _202 Accepted_: Nel caso in cui la feature venga eliminata correttamente.







