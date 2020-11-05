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

Api di creazione degli elementi. codice: rappresenta il codice elemento che deve essere univoco. in caso contrario viene sollevato un errore (HTTP_NOT_MODIFIED) prototype: rappresenta il tipo dell'elemento e deve essere presente nel sistema. Anche in questo caso verrebbe sollevato un errore (HTTP_NOT_FOUND). In base a prototype l'elemento viene inizializzato 

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


