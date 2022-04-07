#Actions
###**POST	_/actions/{feature}/{action}_**
-------------



_params_:

- **feature**: Basic text / string value
- **action**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_usage_:


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







###**PUT	_/actions/{feature}/{action}_**
-------------



_params_:

- **feature**: Basic text / string value
- **action**: Basic text / string value

_result_:

- **format**: JSON (Javascript Serialized Object Notation)
- **content_type**: application/json; charset=utf-8

_usage_:


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








