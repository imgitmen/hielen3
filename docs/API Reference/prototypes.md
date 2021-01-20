#Prototypes
## **/prototypes/**

#### POST
-------------
_params_:

- **prototype**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


** Definizione di nuovi prototipi **
_PLACEHOLDER: Non ancora implementato_






#### GET
-------------
_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Recupero di tutte le informazioni dei prototipi**

ritorna una struttura json di questo tipo:


	"data": {
	    "uid": ...,
	    "module": ...,
	    "struct": {
		"classification": ...,
		"type": ...,
		"parameters": {
		    "par1": {
			"type": ...,
			"operands": {
			    "output": ...
			}
		    },
                    "...",
		    "parN": {
			"type": ...,
			"operands": {
			    "output": ...
			}
		    }
		}
	    }
	}








## **/prototypes/{prototype}**

#### GET
-------------
_params_:

- **prototype**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Alias per il recupero di tutte le informazioni di uno specifico prototipo**







## **/prototypes/{prototype}/forms**

#### GET
-------------
_params_:

- **prototype**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Alias per il recupero di tutte le informazioni delle form di uno specifico prototipo**







## **/prototypes/{prototype}/forms/{form}**

#### GET
-------------
_params_:

- **prototype**: Basic text / string value
- **form**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Alias per il recupero di tutte le informazioni di una specifica form di uno specifico prototipo**







## **/prototypes/{prototype}/struct**

#### GET
-------------
_params_:

- **prototype**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Alias per il recupero delle info di inizializzazione delle features legate ad uno specifico prototipo**







