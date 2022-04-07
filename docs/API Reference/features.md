#Features
###**POST	_/features/_**
-------------



_params_:

- **prototype**: Basic text / string value
- **properties**: JSON Schema {**style**: str|bytes, **status**: str|bytes, **description**: str|bytes, **location**: str|bytes, **context**: str|bytes, **label**: str|bytes, **timestamp**: str|bytes}
- **geometry**: JSON Schema {}

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_usage_:


DESCRIZIONE:

**Creazione delle Features.**

Ogni feature viene creata sulla  il suo il suo prototipo `prototype` ed in fase di creazione viene creato il campo `uid`. Questi due campi sono immutabli. Vedi [PUT feature](#put-featuresuid)

PARAMETRI:

- **prototype**: Definisce il tipo della feature e accetta uno dei valori recuperabili attraverso l'API [GET prototype](../prototypes/#get)

- **properties**: Json dei campi anagrafici della feature, utilizzati dal sistema. Nessuno di essi è obbligatorio. Lo schema è il seguente:


        {
            "context": "Stringa: gruppo in cui inserire la feature",
            "label":  "Stringa: etichetta mnemonica della feature",
            "description": "Stringa: descrizione della feature",
            "location": "Stringa: descrizione mnemonica della posizioni",
            "style": "Stringa: informazioni per le direttive csv",
            "status": "Stringa: informaizoni di stato",
            "timestamp": "Stringa: data di creazione della feature nel formato YYYY-MM-DD HH:MM:SS"
        }


- **geometry** : Accetta un [GeoJson](https://geojson.org/)

OUTPUT:

Se la feature viene creata correttamente la sua struttura viene restituita all'interno del campo `data` del json di risposta standard

RESPONSE CODES:

- _409 Conflict_: Nel caso in cui il uid fornito esista già.
- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _201 Created_: Nel caso in cui la feature venga creata correttamente.






###**GET	_/features/_**
-------------



_params_:

- **uids**: Basic text / string value
- **cntxt**: Basic text / string value
- **info**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_usage_:


DESCRIZIONE:

**Recupero delle informazioni delle features.**

PARAMETRI:

- **uids**: Lista "comma separated" degli id delle features da recuperare. Nel caso in cui non venisse fornito alcun valore, verrebbe fornita in output l'intera lista delle features presenti nel sistema.

- **cntxt**: Lista "comma separated" dei gruppi di features da recuperare. Se presente agisce da filtro rispetto al risultato elaborato in base al parametro _"uids"_ 
- **info**: Lista "comma separated" delle informazioni relative ad ogni feature da includere nella risposta. In generale dei sottoalberi Json. Le classi di informazione disponibili sono:

    - _capabilities_: tipi di interrogazioni eseguibili sulla feature: elenco comprendente una, nessuna o più voci tra queste: _data_, _map_, _cloud_. Vedi [GET query](../query/#get)
    - _parameters_: parametri (timeseries) associati alla feature, interrogabili tramite [GET query](../query/#get)
    - _timeline_: eventuale timeline globale dei parametri della feature

ESEMPIO:

        GET features?cntxt=619d00137303c&info=parameters,capabilities

OUTPUT:

All'interno del campo `data` del json di risposta standard viene restituito un oggetto "chiave, valore" json che é interpretabile come GeoJson estraendo la lista dei values.
L'oggetto contiene tutte le features che rientrano nei criteri di ricerca. Quindi un struttura di questo tipo:

	"features": {
		"1285beb4": {
			"type": "Feature",
        		"properties": {
			    "uid": "1285beb4",
			    "classification": "Source",
			    "context": "619d00137303c",
			    "description": null,
			    "label": "CAM1",
			    "location": null,
			    "status": "0",
			    "style": "9cecce36",
			    "timestamp": "2021-11-10 00:00:00",
			    "type": "PhotoMonitoring",
			    "inmap": null
        		},
        		"parameters": [
				{
					"series": "06578ff5509871eef7e62f8d2bc175de",
            				"param": "Displacement",
            				"unit": "mm",
          			},
          			{
            				"series": "2388b145eed5036e78afff43114cf7f7",
            				"param": "Correlation_Coefficient",
            				"unit": "number",
          			},
        		],
        		"timeline": [
		          "2021-11-04T15:11:45"
        		],
        		"capabilities": [
				"map"
			]
      		},
	}
            

RESPONSE CODES:

- _200 OK_: Nel caso vengano trovate features corrispondenti ai criteri di ricerca
- _404 Not Found_: Nel caso in cui nessuna feature risponda ai criteri di ricerca








###**GET	_/features/{uid}_**
-------------



_params_:

- **uid**: Basic text / string value
- **cntxt**: Basic text / string value
- **info**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_usage_:


DESCRIZIONE:

**Alias di recupero informazioni della specifica feature**

PARAMETRI:

- **info**: Lista "comma separated" delle informazioni relative ad ogni feature da includere nella risposta. In generale dei sottoalberi Json. Le classi di informazione disponibili sono:

    - _capabilities_: tipi di interrogazioni eseguibili sulla feature: elenco comprendente una, nessuna o più voci tra queste: _data_, _map_, _cloud_. Vedi [GET query](../query/#get)
    - _parameters_: parametri (timeseries) associati alla feature, interrogabili tramite [GET query](../query/#get)
    - _timeline_: eventuale timeline globale dei parametri della feature

ESEMPIO:

        GET features/1285beb4&info=parameters,capabilities

OUTPUT:

Vedi [GET features](#get)


RESPONSE CODES:

- _200 OK_: Nel caso vengano trovate features corrispondenti ai criteri di ricerca
- _404 Not Found_: Nel caso in cui nessuna feature risponda ai criteri di ricerca







###**PUT	_/features/{uid}_**
-------------



_params_:

- **uid**: Basic text / string value
- **properties**: JSON Schema {**style**: str|bytes, **status**: str|bytes, **description**: str|bytes, **location**: str|bytes, **context**: str|bytes, **label**: str|bytes, **timestamp**: str|bytes}
- **geometry**: JSON Schema {}

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_usage_:


**Modifica delle properties di una feature**

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _200 Ok_: Nel caso in cui la feature venga modificata correttamente.






###**DELETE	_/features/{uid}_**
-------------



_params_:

- **uid**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_usage_:


**Cancellazione delle Features**

Se la feature viene cancellata correttamente ne restituisce la struttura

Possibili risposte:

- _404 Not Found_: Nel caso in cui il prototipo richiesto non esista.
- _200 Accepted_: Nel caso in cui la feature venga eliminata correttamente.







