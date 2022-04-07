#Actionschemata
###**GET	_/actionschemata/_**
-------------



_params_:

- **prototypes**: Basic text / string value
- **actions**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_usage_:


**Recupero dello schema dei parametri per inizializare le forms delle azioni**

ritorna una struttura json di questo tipo:


        {
            "NomePrototipo1": {
                "action1": {
                    "args": {
                        "arg1.1": "type_arg1.1",
                        "arg1.2": "type_arg1.2",
                        ...
                    },
                    "mandatory": [ args keys sublist ]
                },
                "action2": {
                    "args": {
                        "arg2.1": "type_arg2.1",
                        "arg2.2": "type_arg2.2",
                        ...
                    },
                },
                ...
            },
            "NomePrototipo3": {
                ...
            },
            ...
        },







###**GET	_/actionschemata/{prototype}_**
-------------



_params_:

- **prototype**: Basic text / string value
- **actions**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_usage_:


**Alias per il recupero di tutte le informazioni di uno specifico prototipo**







###**GET	_/actionschemata/{prototype}/{action}_**
-------------



_params_:

- **prototype**: Basic text / string value
- **action**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_usage_:


**Alias per il recupero di tutte le informazioni delle form di uno specifico prototipo**







