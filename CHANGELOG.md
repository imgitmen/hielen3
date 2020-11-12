CHANGELOG
=========



## 2.0.3
### **11 Novembre 2020**
- Modificata api POST `/elements`: la variabile `element` è descritta dalla Classe hielen2.api.data.ElementSchema e validata. In paricolare è stato introdotto l'attibuto `context`
- Modifcata api GET `/data`: la variabile `datamap` è descritta dalla Classe hielen2.api.data.DataMapSchema e validata.

### **9 Novembre 2020**
- Introdotta la classe hielen2.utils.JsonValidable, per la validazione e documentazione automatica dei parametri delle api (JSON Schema descrition) 
- corretti bug minori in hielen2.datalink

### **6 Novembre 2020**
- L'interfaccia DB è ora thread safe!!! (almeno per il dummy json db)

## 2.0.2 
### 4 Novembre 2020
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
 
- L'api `/series` diventa `/data` e cambia il suo comportamento: la variabile di tipo json  _datamap_ si aspetta il campo _series_ invece di _parameters_. In questo campo devono essere inseriti i codici delle serie e non più il costrutto "codice_elemento:parametro_elemento". I codici delle serie si possono recuperarare dall'api `/elements` (vedi Nota successiva)
- L'api `/elements` cambia la sua risposta e per ogni parametro nella lista _parameters_ degli elementi viene agiunto il codice della serie di riferimento che può essere fornito senza modifiche a `/data`:

        {
            "series":<seriescode>,
            "name":<seriesname>,
            "um":<seriesunit>
        }

- **GET** `/series`
- **GET** `/series/{el}`
- **GET** `/series/{el}/{param}`
- **GET** `/prototypes`
- **GET** `/prototypes/{type}`
- **GET** `/prototypes/{type}/forms`
- **GET** `/prototypes/{type}/forms/{form}`
- **POST** `/elements`
- **GET** `/elements`
- **GET** `/elements/{el}`
- **DELETE** `/elements/{el}`
- **PUT** `/elements/{el}`


