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

Api di creazione degli elementi. Ogni elemento deve avere il suo codice univoco `code` e il suo prototipo `prototype`. ####Possibili risposte: - **409 Conflict** in caso il codice fornito esistesse già - **404 Not Found** in caso il prototipo richiesto non venisse trovato - **201 Created** in caso di creazione dell'elemento Il prototipo dell'elemento forisce informazioni per l'inizializazione della struttura 

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


