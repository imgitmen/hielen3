#Actions
## **/actions/{feature}**

#### GET
-------------
_params_:

- **feature**: Basic text / string value
- **actions**: Basic text / string value
- **timestamp**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Recupero dello stato corrente delle azioni effettuate su una feature**

L'intento di questa api è quello di fornire i valori richiesti secondo lo schema dell'azione  
 
___nota 1___: `actions` accetta valori multipli separati da virgola
___nota 2___: A seconda dell'action richiesta, alcuni parametri potrebbero essere utilizzati in fase di input ma non registrati. Il che vuol dire che per quei parametri il valore di ritorno sarà null
 
viene restituito una struttura di questo tipo:

        [
            { "feature"*:...,
              "action_name*":...,
              "timestamp": ...,
              "value":{...}
            },
            { "feature"*:...,
              "action_name*":...,
              "timestamp": ...,
              "value":{...}
            },
            ...
        ]


___nota 3___ :(*) I campi "feature" e "action" potrebbero non essere restituiti nella struttura nel caso in cui essi risultino non ambigui. "timestamp" e "value" vengono sempre restituiti

Possibili risposte:
 
- _404 Not Found_: Nel non venga trovata la feature richiesta o essa abbia un problema di configurazione








## **/actions/{feature}/{action}**

#### GET
-------------
_params_:

- **feature**: Basic text / string value
- **action**: Basic text / string value
- **timestamp**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


    **Recupero dello stato corrente per una specifica azione di una specifica feature**





#### DELETE
-------------
_params_:

- **feature**: Basic text / string value
- **action**: Basic text / string value
- **timestamp**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


    **Eliminazione di una determinata azione di una secifica feature**





#### POST
-------------
_params_:

- **feature**: Basic text / string value
- **action**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_description_:


**Esecuzione delle azioni**

Richiede l'esecuzione di una specifica azione su una feature, fornendo tutte le informazioni necessarie attraverso una form dinamica dedicata.

- Oltre ai due parametri `feature` e `form`, `timestamp`, indicati nella url, accetta un _multipart/form-data_ basato sulla specifica form, selezionata tramite i due parametri espliciti.
- Tutto il content è scaricato attarverso i chunk dello stream ('100 continue') per evitare il timeout dei workers in caso di contenuti di grandi dimensioni.

Possibili risposte:

- _200 OK_: Nel caso in cui l'azione vada a buon fine. L'azione richiesta viene presa in carico ma potrebbe avere un tempo di esecuzione arbitrario. L'azione quindi viene splittata su un altro processo.
- _404 Not Found_: Nel caso la feature non esista o non sia definita per essa l'azione richiesta.
- _500 Internal Server Error_: Nel caso pessimo che il modulo dichiarato non esista.
- _501 Not Implemented'_: Nel caso la tipologia non fornisse ancora l'iplementazione di uno o tutti i moduli di gestione


E' stato implementato il meccanismo minimo di gestione che prevede il salvataggio delle info fornite che possono essere fornite tali e quali in uscita (vedi metodo GET dell'api). Questo meccanismo permette di svluppare i moduli a partire da un template con risposta di default.








