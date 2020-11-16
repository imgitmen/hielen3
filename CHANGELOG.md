CHANGELOG
=========

## **v2.0.4**
### **16 Novembre 2020**
- introduzione dello Schema GeoJson per la validazione

### **13 Novembre 2020**
- rinominazione DELETE `/elements` -> DELETE `/features`.
- eliminazione degli alias GET `/features/{context}` e `/features/{context}/{uid}` a causa del conflitto l'entry point DELETE `/features`. Il passaggio del context sarà esclusivmante attraverso il parametro cntxt (__nota__: questo nome è dovuto alla collisione del nome con il campo 'context' dell'oggetto request). In caso lo possiamo cambiare.
- introduzione dell'alias `/features/{uid}` per il recupero delle info della specifica Feature.

### **12 Novembre 2020**
- ovunque nel mondo il parmetro 'uuid' (universal unique id) diventa 'uid'.
- rinominazione POST `/elements` -> POST `/features`.
- rinominazione GET `/elements` -> GET `/parameters` e modifica uscita in questo schema:

        {
            <feature1_UID>:[
                {
                    "series":<feature1_param1_series_UID>,
                    "param":<feature1_param1_name>,
                    "um":<feature1_param1_measurement_unit>
                },

                ...

                {
                    "series":<feature1_paramN_series_UID,
                    "param":<feature1_paramN_name>,
                    "um":<feature1_paramN_meaurement_unit>

                }
            ],

            ...

            <featureX_UID>:[
                {
                    "series":<featureX_param1_series_UID>,
                    "param":<featureX_param1_name>,
                    "um":<featureX_param1_measurement_unit>
                },

                ...

                {
                    "series":<featureX_paramM_series_UID,
                    "param":<featureX_paramM_name>,
                    "um":<featureX_paramM_meaurement_unit>

                }
            ]
        }

- introduzione api `/features` con lo schema usato da Daniele e SimoneD:
    
    GET `/features` 

    GET `/features/{context}/`

    GET `/features/{context}/{feature}`


    _uscita_:

    nota 1: viene introdotto ___"context"___ allo stesso livello di features.

    nota 2: ___"cod"___ diventa ___"label"___.

    nota 3: dalle properties vengono elminate ___"z"___ e ___"mslm"___.

    nota 4: ___"state"___ viene mantenuto ma per ora è inutilizzato

        {
            "context":<context_name>,
            features": [
                {
                    "type": "Feature",
                    "properties": {
                    "uid": ...,
                    "label": ...,
                    "date": ...,
                    "type": ...,
                    "style": ...,
                    "state": ...
                },
                    "geometry": <GeoJson Validable>
                },

                ...
                
                {
                    "type": "Feature",
                    "properties": {
                        "uid": ...,
                        "label": ...,
                        "date": ...,
                        "type": ...,
                        "style": ...,
                        "state": ...
                    },
                "geometry": <GeoJson Validable>
            }
        ]
    }


## **2.0.3**
### **11 Novembre 2020**
- Modificata api POST `/elements`: la variabile `element` è descritta dalla Classe hielen2.api.data.ElementSchema e validata. In paricolare è stato introdotto l'attibuto `context`
- Modifcata api GET `/data`: la variabile `datamap` è descritta dalla Classe hielen2.api.data.DataMapSchema e validata.

### **9 Novembre 2020**
- Introdotta la classe hielen2.utils.JsonValidable, per la validazione e documentazione automatica dei parametri delle api (JSON Schema descrition) 
- corretti bug minori in hielen2.datalink

### **6 Novembre 2020**
- L'interfaccia DB è ora thread safe!!! (almeno per il dummy json db)

## **v2.0.2**
### **4 Novembre 2020**
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


