CHANGELOG
=========

### **30 Dicembre 2020**
- sviluppo (non completo) di config hielen2.ext.PhotoMonitoring: 
- Implementato il metodo di recupero e settaggio delle informazioni geometriche/geografiche dell'immagine in ingresso
- Aggancio del codice originale per la gesgione del netcdf (in debug)

### **22 Dicembre 20202**
- Delineata la gestione di mappa delle immagini prodotte: Ogni immagine prodotta sarà sempre associata al suo `crs` e la matrice di trasformazione affine, anche nele caso in cui queste informazioni non dovessero essere passate in configurazione. In questo caso si assume un piano cartesiano con udm in m e una matrice identità per le trasformazioni affini. Sarà dunque sempre possibile gestire le immagini come mappe (slippy maps) e sfruttare la tassellazione, il cacheing dei tasselli.

### **20 Dicembre 2020**
- Modificata l'api POST `/actions/{feature}/{form}` in modo da interrogare la Source (per ora solo PhotoMonitoring) sulla definizione delle azioni:
- Implementate le classi di Schema per config e feed per il modulo `hielen2.ext.PhotoMonitoring`. **ATTENZIONE** per _config_: introdotto il campo "timestamp", eliminati i campi espliciti relativi al word_file (`word_file` mantenuto), modificato il campo `epsg` in `csr`.

### **15 Dicembre 2020**
- Delineato il modello di scrittura dei Source plugin secondo un template univoco. Ogni plugin potrà essere un modulo python definito come segue:

**deve** definire tante classi `marshmallow.Schema` quante sono le azioni che vengono prese in carico dal Template. [Marsmallow](https://github.com/marshmallow-code/marshmallow) è un serializzatore di oggetti python. Lo schema definito servirà per definire i campi in ingresso per ogni azione e fare i check dei valori in ingresso.

Il nome delle classi Schema **deve** seguire questa sintassi: `class {Action}Schema(marshmallow.Schema)` dove {Action} è il nome dell'azione (es.: config, feed, ..) con l'iniziale _maiuscola_.
Nella classe vengono definiti i tipi dei campi (`marshmallow.fields` cfr. https://marshmallow.readthedocs.io/en/stable/ ). ATTENZIONE: in caso fosse necessario l'ingresso di file o comunque oggetti blob dovrà essere utilizzato come field la classe `hielen2.utils.LocalFile`. In questo modo il sistema risolverà la chiamata API salvando in locale lo stream dei dati associato a quel determinato field, il quale sarà accessibile al template attraverso un path che verrà fornito insieme agli altri campi al momento della chiamata del metodo di gestione dell'azione (vedi sotto).

**deve** implementare una classe `Source(hielen2.datalink.HielenSource)` che esponga tanti metodi quante sono le dichiarazioni di Schema seguendo questa sintassi: il metodo di gestione dell'azione **deve** chiamarsi come l'azione stessa ( tutto in _minuscolo_ ). Le classi estese sfrutteranno il metodo `__init__` della superclasse in modo da avere a disposizione tutto quello di cui necessitano.

Questo modello permette di svincolare i template dalla necessità di conoscere a priori le azioni ammmissibili per il sistema. Infatti, facendo introspezione su un template che segua le regole di sintassi sarà sempre possibile conoscere le azioni definite ed esternalizzarle al front-end che in base alle definizioni delle classi di Schema delle azioni, sarà sempre in grado di instanziare una form adeguata.

## **v2.0.5**
### **9 Dicembre 2020**
- Implementata **working** POST `/actions/{feature}/{form}` tramite content-type/multipart dinamico definito dal prototipo: L'api è collegata ai moduli reali delle tipologie definiti come templates, con la funzionalità minima di salvare i parametri in ingresso. I moduli sono in fase di sviluppo e man mano che vengono implementati le funzionalità aumenteranno. 
- Implementato Loading dinamico dei moduli di elaborazione definiti come estensioni di `hielen2.datalink.HielenSource`
- Implementata **working** GET `/actions/{feature}[/{form}]`: Per ogni form richiesta, risponde con tutti i parametri definiti nel relativo prototipo, riempiti con i valori definiti tramite la POST della stessa api. I valori non precedentemente forniti vengono impostati a null
- Riveduta e corretta GET `prototypes/{prototype}/forms[/form]`: **ATTENZIONE** adesso risponde con TUTTI i campi dentro il dizionario "args" e comunica i campi obbligatori attraverso l'array "mandatory". Questa struttura è più versatile in quanto, una volta definito il set completo degli argomenti, è possibile definire un numero arbitrario di sottoinsiemi predicativi non necessariamente distiniti: Oltre al sottoinsieme "mandatory" si potrebbe, ad esempio, definire un sottoinsieme di immutabili. Qui sotto una struttura di esempio:

        {
            "data": {
                "args": {
                    "epsg": "string",
                    "master_image": "file",
                    "negative_pixel_y_size": "string",
                    "pixel_x_size": "string",
                    "rotation_about_the_x_axis": "string",
                    "rotation_about_the_y_axis": "string",
                    "step_size": "string",
                    "window_size_change": "string",
                    "world_file": "file",
                    "x_coordinate_of_upper_left_pixel_center": "string",
                    "y_coordinate_of_upper_left_pixel_center": "string"
                },
                "mandatory": [
                    "master_image",
                    "step_size",
                    "window_size_change"
                ]
            },
            "meta": {
                "data_type": "GET /prototypes/PhotoMonitoring/forms/config",
                "message": "",
                "response": "ok"
            }
        }


### **7 Dicembre 2020**
- Rimodellato il feature db per contenere gli argomenti delle actions
- Riveduto il _feature_proto_ db: Inserito il  modulo di riferimento tra le info del prototipo (il modulo contenete la classe estesa di `hielen2.datalink.HielenSource`)
- Definita la superclasse `hielen2.datalink.HielenSource` con definizione univoca di `__init__` con questo footprint: `(self,featureobject,environment)`. La classe definisce inotre i metodi astratti che vengono utilizzati dal sistema che ogni estensione di questa dovrà implementare.


### **2 Dicembre 2020**
- Struttura definitiva delle features:
        
        {
            "properties":"..."
            "parameters":"..."
            "geometry":"..."
        }

dove:

___properties___ mantiene **tutte** le info della feature. Quelle di base: `uid`,`type`,`classification`,`location`,`description` e quelle definite per le specifiche azioni definite per la tipologia. In particolare quella di configurzione.

___parameters___ mantiene la struttura di accesso alle info e ai dati dei parametri definiti per la feature.

___geometry___ fornisce le informazioni geometriche della feature.

Rivedute le api `/actions`, `/parameters`, `/features` (`/data` da rivedere)

### **24 Novembre 2020**
- Implementate **dummy** `/actions/{feature}/` e `/actions/{feature}/{form}`

### **23 Novembre 2020**
- Riorganizzato il db delle features per permettere una gestione più razionale

### **19 Novembre 2020**
- riorganizzata la struttura per la gestione delle classi estese che necessitano di dynamic loading: nel modulo himada2.ext (cartella) vengono raccoliti per comodità gli oggetti che saranno implementati man mano come estensione di superclassi astratte appositamente definite: per ora hielen2.datalink.Source e hielen2.datalink.DB e hielen2.datalink.DataCache. Oltre alle classi in hielen2.ext, il sitema potrà utilizzare moduli esterni che estendano le superclassi elencate.
- inserito 'timestamp' nello schema json accettato da POST `/feature` e PUT `/feature`.
- risolto bug minore di incoerenza su GET `/data/{feature}` e `/data/{feature}/{parameter}`. Quest'ultima continua ad accettare uno tra i nomi dei parametri della feature. Entrambe rispondo intestando le colonne in uscita con lo uid della serie, come GET `/data/`.

### **17 Novembre 2020**
- Implementata **dummy** POST `/actions/{feature}/{form}`: 

## **v2.0.4**
### **16 Novembre 2020**
- per coerenza rivisti i parametri di POST `/feature`:

		uid:<string>
		prototype:<string>
		properties:<json schema Properties>
		geometry:<json schema GeoJson>

- analogo discorso per  PUT `/feature/{uid}`:

		properties:<json schema Properties>
		geometry:<json schema GeoJson>

- sistemata la risposta di GET `/feature`, modificando il livello di "geometry"
- implementata api PUT `/features/{uid}`. Accetta il paramentro `properties` con uno schema analogo al parmetro `feature` di POST `/features` con queste differenze: **nello schema della PUT, `uid` e `prototype` NON vengono accettati perchè sono campi chiave della feature e non possono essere modificati**. lo `uid` della feature deve essere specificato come url e non come parametro.
- introduzione dello Schema GeoJson per la validazione
- modificata POST `/features/` per accettare un GeoJson nell'attibuto `geometry` del Json principale `feature`

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

    nota 1: NON viene introdotto ___"context"___, come invece preventivato

    nota 2: ___"cod"___ diventa ___"label"___.

    nota 3: ___"date"___ diventa ___"timestamp"___

    nota 3: dalle properties vengono elminate ___"z"___ e ___"mslm"___.

    nota 4: ___"state"___ viene mantenuto ma per ora è inutilizzato

        {
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "uid": ...,
                        "label": ...,
                        "context":...,
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
                            "context": ...,
                            "date": ...,
                            "type": ...,
                            "style": ...,
                            "state": ...
                        },
                    "geometry": <GeoJson Validable>
                }
            ]
        }


## **v2.0.3**
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


