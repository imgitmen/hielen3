#Parameters
## **/parameters/**

#### GET
-------------
_params_:

- **uids**: Basic text / string value
- **params**: Basic text / string value
- **cntxt**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


    **Ricerca dei parametri associati alle features**.

    __nota__: uid accetta valori multipli separati da virgola

    viene restituita una struttura di questo tipo:

            {
                "<fetUID>":[
                    {
                        "series":"<series_UID>",
                        "param":"<param_name>",
                        "um":"<mearurement_unit>"
                    }
                    ...
                ]
                ...
            }


    Possibili risposte:

    - _404 Not Found_: Nel caso in cui nessun parametro risponda ai criteri


    






## **/parameters/{uid}**

#### GET
-------------
_params_:

- **uid**: Basic text / string value
- **params**: Basic text / string value
- **cntxt**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


    **Alias di ricerca dei Parametri della specifica Feature**






## **/parameters/{uid}/{param}**

#### GET
-------------
_params_:

- **uid**: Basic text / string value
- **param**: Basic text / string value
- **cntxt**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


    **Alias di ricerca dello specifico Parametro della specifica Feature lo specifico contesto**






