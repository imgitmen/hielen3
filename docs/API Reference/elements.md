#Elements
##/elements/
####POST
_params_:

- **element**: JSON Schema {**geom**!: str|bytes, **description**!: str|bytes, **uuid**!!: str|bytes, **label**!: str|bytes, **style**!: str|bytes, **context**!: str|bytes, **prototype**!!: str|bytes, **status**!: str|bytes}

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Api di creazione degli elementi.**

Ogni elemento deve avere il suo codice univoco `uuid` e il suo prototipo `prototype`. Il prototipo dell'elemento forisce informazioni per l'inizializazione della struttura.

Possibili risposte:

- _409 Conflict_: Nel caso in cui il codice fornito esista già.
- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _201 Created_: Nel caso in cui l'elemento venga creato correttamente.


####GET
_params_:

- **elist**: Basic text / string value
- **context**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8


##/elements/{uuid}
####GET
_params_:

- **uuid**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

####DELETE
_params_:

- **uuid**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8


