CHANGELOG
=========
## 2.0.2 November 6 2020
- L'interfaccia DB è ora thread safe!!! (almeno per il dummy json db)
- Implementata la documentazione automatica delle api
- Implementate le api **POST** `../elements` e **DELETE** `../elements`
- L'uscita per tutte le api element (e per tutte le api con risposta json in generale), seguirà questo schema:

		{
			"meta": {
				"data_type": "DELETE /elements/ciao",
				"response": "ok"
				"message": "",
    		},
    		"data":{
				...
			}
		}
 
- L'api `../series` diventa `../data` e cambia il suo comportamento: la variabile di tipo json  _datamap_ si aspetta il campo _series_ invece di _parameters_. In questo campo devono essere inseriti i codici delle serie e non più il costrutto "codice_elemento:parametro_elemento". I codici delle serie si possono recuperarare dall'api `../elements` (vedi Nota successiva)
- L'api `../elements` cambia la sua risposta e per ogni parametro nella lista _parameters_ degli elementi viene agiunto il codice della serie di riferimento che può essere fornito senza modifiche a `data`:

        {
            "series":<seriescode>,
            "name":<seriesname>,
            "um":<seriesunit>
        }
