#Elements
##/elements/
####POST
_params_:

- **code**: Basic text / string value
- **prototype**: Basic text / string value
- **geom**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Api di creazione degli elementi.**

Ogni elemento deve avere il suo codice univoco `code` e il suo prototipo `prototype`. Il prototipo dell'elemento forisce informazioni per l'inizializazione della struttura.

Possibili risposte:

- _409 Conflict_: Nel caso in cui il codice fornito esista già.
- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _201 Created_: Nel caso in cui l'elemento venga creato correttamente.


####GET
_params_:

- **elist**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8


##/elements/{code}
####GET
_params_:

- **code**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

####DELETE
_params_:

- **code**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8


