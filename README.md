# HIELEN

Hielen (HIerarchical ELaboration ENgine) è una suite di api REST dedicata alla rappresentazione e alla gestione delle evoluzioni temporali di fenomeni dotati di caratteristiche spaziali.
Essa è stata modellata sulle esigenze del monitoraggio strutturale, ambientale e geognostico, con l'obiettivo di astrarre lo strato fisico degli acquisitori installati sul campo e fornire un ambiente omogeneo per l'analisi dei dati relativi all'evoluzione dei fenomeni monitorati.

## Note generali sulle API

### 1. Costruzione della URL
In questo documento si farà riferimento alle specifiche api in questo modo:
        
    PROTOCOLLO /{nomeapi}

intendendo con questa scrittura il protocollo da utilizzare per la chiamata (vedi punto 2) e il punto d'ingresso della specifica api che dovrà essere utlizzato nella _url_, accodandolo allo _hostname_ e all' _endpoint_ specifici. es.:

supponedo

_hostname_ = ___www.hostname.com___

_endopoint_ = ___api/hielen___

_nomeapi_ = ___features___

la costruzione della _url_ sarà la seguente


    www.hostname.com/api/hielen/features


dove la parte `www.hostname.com/api/hielen` sarà il punto d'ingresso per tutte le api della specifica installazione e dipenderà esclusivamente dalla configurazione del webserver che ospita la suite


### 2.  Utilizzo dei potocolli standard HTTP
Le API seguno le direttive REST e dunque ognuna di esse sfrutta i diversi protocolli http per svolgere azioni differenti. In generale:

**POST** per la creazione di un nuovo elemento

**GET** per il recupero di informazioni di uno o più elementi

**PUT** per la modifica di un elemento 

**DELETE** per l'eliminazione di un elemento

ad esempio

    POST www.hostname.com/api/hielen/features?...

potrà essere utilizzato per creare un elemento di tipo feature. mentre

    GET www.hostname.com/api/hielen/features/uuid_feature

servirà a recuperare le informazioni della feature individuata da _uuid_feature_

### 3.  Risposta standard delle API
Dove non diversamente specificato, le api rispondono con un json in questo formato:

    {
		"meta": {
    		"response": ...,
    		"message": ...,
    		"data_type": ...,
  			},
		"data": ... 
	}

dove:

-   il campo __meta__ contine informazioni relative all'esecuzione della richiesta .
-   il sottocampo __response__ può assumere i valori `error` oppure `ok`.
-   il sottocampo __message__ contiene l'eventuale messaggio di errore.
-   il sottocampo __data_type__ contiene la marcatura dell'api richiesta (es.: "GET /api/hielen/features").
-   il campo __data__ contiene la risposta prodotta dall'esecuzione, generalmente un json, se essa è andata a buon fine.


## Struttura generale delle API

Protocollo | Nome API | Descrizione
-------- | ---------- | -----------
GET | [/prototypes](docs/API Reference/prototypes/#prototypes_1) | informazioni sulle tipologie di feature implementate
GET | [/actionschemata](docs/API References/actionschemata/#actionschemata_1) | schemi di base per agire sulle features
POST | [/features](docs/API Reference/features/#post) | creazione di una nuova feature
GET | [/features](docs/API Reference/features/#get) | recupero di informazioni sulle features
PUT | [/features](docs/API Reference/features/#put) | modifica di una feature
DELETE | [/features](docs/API Reference/features/#delete) | eliminazione di una feature
POST | [/actions](docs/API Reference/actions/#post) | azione specifica su una featrue 
GET | [/actions](docs/API Reference/actions/#get) | recupero di informazioni sull'azione eseguita su una feature
PUT | [/actions](docs/API Reference/actions/#put) | modifica di un'azione precedentemente eseguita su una feature
DELETE | [/actions](docs/API Reference/actions/#delete) | eliminazione di un'azione precedemente eseguita su una feature
GET | [/query](docs/API Reference/query/#get) | interfaccia di interrogazione dei dati


