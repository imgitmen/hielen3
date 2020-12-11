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


            {
                "NomePrototipo1": {
                    "forms": {
                        "form1": {
                            "args": {
                                "arg1.1": "type_arg1.1",
                                "arg1.2": "type_arg1.2",
                                ...
                            },
                            "mandatory": [ args keys sublist ]
                        },
                        "form2": {
                            "args": {
                                "arg2.1": "type_arg2.1",
                                "arg2.2": "type_arg2.2",
                                ...
                            },
                        },
                        ...
                    },
                    "module": subclass of hielen2.datalink.HilenSource,
                    "struct": {
                        "parameters": {
                            "param1": {
                                "operands": {
                                    "output": "parameter1 name"
                                },
                                "type": "series type"
                            },
                            "param2": {
                                "operands": {
                                    "output": "parameter2 name"
                                },
                                "type": "series type"
                            },
                            ...
                        },
                        "properties": {
                            "classification": feature classification,
                            "type": feature type
                        }
                    }
                },
                "NomePrototipo3": {
                    ...
                },
                ...
            },

    






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







