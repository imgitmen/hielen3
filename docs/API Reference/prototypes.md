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
            {
                "uid1": ...,
                "module1": ...,
                "struct": {
                    "classification": ...,
                    "type": ...,
                    "parameters": {
                        "par1_1": {
                            "type": ...,
                            "operands": {
                                "output": ...
                            }
                        },
                        "...",
                        "par1_N": {
                            "type": ...,
                            "operands": {
                                "output": ...
                            }
                        }
                    }
                }
            },
            {
                "uid2": ...,
                "module2": ...,
                "struct": {
                    "classification": ...,
                    "type": ...,
                    "parameters": {
                        "par2_1": {
                            "type": ...,
                            "operands": {
                                "output": ...
                            }
                        },
                        "...",
                        "par2_N": {
                            "type": ...,
                            "operands": {
                                "output": ...
                            }
                        }
                    }
                }
            }
        }







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







