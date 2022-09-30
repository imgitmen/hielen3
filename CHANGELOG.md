CHANGELOG
=========
## **v3.2.9**
### 30 Settembre 2022
- sistemate threshold canale (chiave uuid,label,tipo(UPPER,LOWER))
- definto json di configurazione generale dei canali come collezione di oggetti
- rilassato il concetto di opernado di una serie permettendo valori arbitrari e non solo uuid di serie (viene riconoesciuto il formato uuid e caricata la serie)
- implementati gli sghembi


## **v3.2.5**
- definito srumento generico con configurazione multipli canali


## **v3.2.4**
### **5 Giugno 2022**
- inserito management soglie (sigolo valore) multiple e range apertura grafici



## **v3.2.3**
### **24 Maggio 2022**
- rivisto l'output di query con uscita json secondo le specifiche di dygraph per il frontend:


    {
        "id1":[
            ["data",valore],
            ["data",valore],
            ...
        ],
        "id2":[
            ["data",valore],
            ["data",valore],
            ...
        ],
        ...
    }

## **v3.2.2**
### **18 Maggio 2022**
- introdotto concetto di ordinal dei parametri associati alle feature:
modificato hielen3.Feature, hielen3.ext.feature_instrument_piezometer
modificato database: aggiunta colonna ordinal alla tabella feature_parameter e modificata la vista v_features_parameter per ordinare i parametri


## **v3.2.1**
### **17 Maggio 2022**
- feature piezometer
- feature shapearray


## **v3.2.0**
### **10 Maggio 2022**
- ristrutturato in modello di astrazione delle feature
- implementazione del modulo di base `hielen3.ext.feature_instrument`
- implementazione del module di base `hielen3.ext.feature_datetree_filesystem_source` che permette la configurazione delle sorgenti basate su strutture di files organizzate secondo il pattern SOURCE/YYYY/MM/DD


## **v3.1.6**
### **21 Aprile 2022**
- implementazione dell'api GET /queue/
- implementazione della capability "stream"
- gestione delle richieste kynetics

## **v3.1.0**
### **5 Marzo 2022**
- modifica api `POST /feature/`: non prende più il parametro **"uid"**. Il campo "uid" della feature viene ora generato dalla chiamata, secondo gli standard di "uuid".
- modifica definizione della classe `hielen3.api.feature.FeaturePropertiesSchema`: rinominato il campo **"context"** in **"milieu"**. Questo coinvolge la chiamata API `POST /feature/` in quanto la classe modificata gestisce e valida il json da passare al parametro `properies` dell'API.
- modifica api `POST,GET,PUT,DELETE /feature/`: rinominato il parametro **"cntxt"** in **"milieu"**. La parola "milieu" al contrario di "context" non dà problemi di interpretazione al sottostante strato di "Hug" (per questo motivo era stata utilizzata "cntxt"). In questo modo vengono uniformati i parmametri di queste API con il campo della classe di gestione delle properties.

## NOTA
- Da reintegrare reintegrare seconda metà 2021 -> inizio 2022

## **v2.0.10**
### **10 Maggio 2021**

- Integrazione di ColorMap, e Config Time Operands


### **7 Maggio 2021**

- Introduzione della classe marshmallow "ColorMap" per la serializzazione delle informazioni custom di colorazione dei dati: tra i vari campi che possono essere ritornati da actionschemata ora ne esiste uno chiamato **ColorMap**. Es.: [PhotoMonitoring actionschemata](https://development.imgback.com/api/hielen2/actionschemata/PhotoMonitoring)

_Come funziona ColorMap_:

Incontrando il campo definito come "ColorMap" all'interno di una risposta di `actionschemata`, il front-end aprirà l'interfaccia di scelta dei colori.
Il risultato dell'interazione dovrà essere sintetizzato in un json da fronire come parametro all'azione corrispondente. Il json dovrà essere nella forma di un array di lunghezza variabile di COPPIE (valore,colore):

	[
		[
			valore,
			colore
		],
		[
			valore,
			colore,
		]
		...
	]


dove:

`valore` è un numero di qualsiasi genere con punto decimale

`colore` è una stringa di colore hex

esempio:

    [
        [
            -0.25,
            '#FFFF00'
        ],
        [
            -0.125,
            '#00FF00'
        ],
        [
            0,
            '#0000FF'
        ],
        [
            0.5,
            '#FF00FF'
        ],
        [
            1,
            '#AEBD00'
        ],
                                                ]

Un array del genere verrebbe inteso in questo modo:

[-inf,-0.25) : ![#FFFF00](https://via.placeholder.com/15/ffff00/000000?text=+)

[-0.25,-0.125) : ![#FFFF00](https://via.placeholder.com/15/ffff00/000000?text=+) --> ![#00FF00](https://via.placeholder.com/15/00ff00/000000?text=+)

[-0.125,0.0) : ![#00FF00](https://via.placeholder.com/15/00ff00/000000?text=+) --> ![#0000FF](https://via.placeholder.com/15/0000ff/000000?text=+)

[0.0,0.5) : ![#0000FF](https://via.placeholder.com/15/0000ff/000000?text=+) --> ![#FF00FF](https://via.placeholder.com/15/ff00ff/000000?text=+)

[0.5,1.0) : ![#FF00FF](https://via.placeholder.com/15/ff00ff/000000?text=+) --> ![#AEBD00](https://via.placeholder.com/15/aebd00/000000?text=+)

[1.0,inf) : ![#AEBD00](https://via.placeholder.com/15/aebd00/000000?text=+)



L'informazione sulla colormap può essere associata ad ongi singola serire dati e può essere fornita in front-end su richiesta: allo scopo L'API `features` è stata modificata in modo da fornire la colormap insieme con i parametri delle features specificando l'opzione info=parameters,...

[esempio (vedi chiamata)](https://development.imgback.com/api/hielen2/features/esempio4?info=parameters):

    {
        ...,
        "parameters": [
            {
                "series": "2b6c9efb4e83f64e757ce862f8b6c2e0",
                "param": "East-West_Displacement",
                "unit": "mm",
                "cmap": [
                    [
                        -0.25,
                        "#FFFF00",
                        0
                    ],
                    [
                        -0.125,
                        "#00FF00",
                        10
                    ],
                    [
                        0,
                        "#0000FF",
                        20
                    ],
                    [
                        0.5,
                        "#FF00FF",
                        60
                    ],
                    [
                        1,
                        "#AEBD00",
                        100
                    ]
                ]
            },
            ...
        ],
        ...
    }

    
dove ogni `cmap` è un array ordinato di triplette utile alla creazione della relativa colorbar. Ogni tipletta fornisce questa infromazione:

`cmap[x][0]`: etichetta del valore, possibilmente da piazzare sulla colorbar alla giusta posizione.

`cmap[x][1]`: colore in esadecimale.

`cmap[x][2]`: posizione dell'ancora del gradiente per il rispettivo colore, nonché per l'eventuale etichetta del valore. La posizione è espressa in percentuale sull'intera colorbar.


### **30 Aprile 2021**
- Gestione generalizzata degli operandi "config time" per i parametri: Ora la classe Source espone dei metodi per dare la possibilità alle sotto classi di definire operandi di elaborazione custom.

## **v2.0.9**
### **22 Aprile 2021**

- implementata l'interrogazione tramite GeoJson
- Correzione di molti bugs
- Aggancio della query dati

## **v2.0.8**
### **2 Aprile 2021**

- implementato il modello di cache per la gestione dei dati prodotti
- debug delle nuove funzionalità

### **31 Marzo 2021**

- inserita la nuova entità db "feaures_info"
- riviste le api 

`/features/`
`/actions/`
`/query/`

- rivisto il codice di 

`hielen2.source`
`hielen2.query`

introdotto il modulo

`hielen2.mapmanager` per la gestione della generazione dei mapfile

- rivisto il codice di

`hielen2.ext.source_photomonitoring`


### **29 Marzo 2021**

inserito il concetto di "info" nelle richieste a feature: Con questo parametro si riescono a centralizzare le chiamate che si focalizzano sulle feature e si separano le informazioni di secondo livello ad esse legate. In questo modo la risposta di default risulta piuttosto leggera ma diventa uno strumento potente e versatile specificando esplicitamente l'estrazione di iformazioni accessorie. Attualmente il parametro "info" accetta un array in cui può essere richiesta l'estrazione di queste info:

- _geometry_: il GeoJson della geometria della feature
- _capabilities_: le possibili interrogazioni effetuabili sulla feature è un array che contiene uno o più di questi valori: "data","map","cloud". la feature risponderà a chiamate del tipo `/query/{capability}`. Nel caso l'array fosse vuoto la feature non risponderebbe ad alcuna interrogazione.
- _parameters_: l'elenco dei parametri associati alla feature come riportati dal'API GET `/parametes/`. Quest'ultima API diviene inutile e sarà eliminata in futuro
- _timeline_: la timeline dei dati associati ai parametri della feature. Utile per lo più per le query map e cloud
- _data_: informazioni specifiche di per la capability "data"
- _map_: informazioni specifiche per la capability "map" (il formato è esattamente quello del nodo "map" del backbone di geoframe)
- _cloud_: informazioni specifiche per la capability "cloud"


### **23 Marzo 2021**

- unificata la struttura di backend che gestisce le chiamate alle serie (dati, mappe e in futuro clouds): Eliminati moduli `hielen2.data.data_access_layer` e `hielen2.maps.data_access_layer` e sostituiti entrambi con `hielen2.query`, il modulo dichiara la classe `hielen2.quert.Series` che prevede il parametro `capability` per distingure tra ["data","map","cloud"]. 
- riviste le api GET `/maps/` e GET `/data/`, unificate sotto l'api GET `/query/` in questo modo:

    GET `/query/data/`
    GET `/query/map`
    GET `/query/cloud/` (futura)

la parametrizzazione di "datamap" viene modificata eliminando "timeto" e "timefrom" ed inserendo "times" come slice temporale (vedi 11 Marzo 2021)

ATTENZIONE: Nel caso venga richesto in risposta un mimetype "txt" il separatore dei campi passa da "," a ";"



### **19 Marzo 2021**
- Revisione dell'ambiente di produzione e accenzione delle istanze su server Nhazca.
- Mapserver: istanza mapserver con workers (vedi Ecoplame) per la gestione delle mappe statiche tassellate (chiamate wms standard)

## **v2.0.7**
### **15 Marzo 2021**
- API: GET `/maps/` per la generazione delle mappe.

### **11 Marzo 2011**
- Introdotti gli slice temporali come estenzione di marshmallow.field mappati sulla classe slice di python:

        Provides python object which performs selection on narry. It axcept a three filed
        string separated by ":".

        ":" presence is managed as:
             
        "start:stop:step"
             
        ie.: 
             
            "start:stop" - extracts from start to stop
             
            "start:" - extracts from start to max 
             
            "start" - extract exactly start
           
- implementato /maps/data_access_layer.py per la gestione angostica delle mappe (utilizzo della datacache)

### **3 Marzo 2021**
- API: DELETE `/actions/{feature}/{*}` agganciata a datacache (vengono tolte dalla cache le elaborazioni dipendenti da config)
- API: DELETE `/features/{feature}` pulizia cache e serie dati

### **25 Febbraio 2021**
- Impelementazione del modulo astratto datacache. Necessario per lo storing delle serie dati. Attualmente implementato con json e csv su flesystem. Potrà essere implementato con Redis.

### **18 Febbraio 2021**
- Implementazione metodo astratto map che viene invocato in modo agnostico sull'istanza di un tipo con capability "map" per produrre le immagini elaborate. Risponde in modo standard creando l'immagine in posizione definita. Nota: Deve diventare metodo di classe 


### **12 Febbraio 2021**
- Revisione del modello di Source con sottoclassi source->data->map->cloud: Ogni sottoclasse estende le funzionalità in modo da avere livlli di capabilities gerarchici ("cloud" ⊃  "map" ⊃  "data"). Di fatto si può intendere ogni tipologia di elaborazione come timeseries la cui produzione è legata alla specifica capability della tipologia di sorgente (es: le mappe elaborate del parametro "displacement" di una specifica feature da una certa data ad un'altra ).
- Esteso il concetto di interrogazione con risultanza di series per data, maps, e clouds

## **v2.0.6**
### **7 Febbraio 2021**
Sviluppo Tinsar Implementata la richiesta di Nhazca:
- Anticipata analisi di potree e generazione / colorazione clouds.
- Implementato mockup 3D funzionante
- Compilazione e utilizzo di PotreConverter


### **27 Gennaio 2021**
- Inserita la validazione dei campi delle action 

### **25 Gennaio 2021**

- Inserito il campo "hint" nella risposta di GET `/actionschemata[/{feature}[/{action}]]`

- Implementata astrazione di DELETE `/actions/{feature}/{action}/`. 

    Prima della rimozione della specifica azione dal db, vengono chimati i metodi preposti alla gestione della rimozione delle informazioni in cache, che si presuppone siano implemetati dai relativi moduli. I moduli possono implementare questi metodi solo se necessario.

    Sintassi:

    Invocando il metodo deleteActionValues(self,action,timestamp) della superclasse Hielen2.Source, essa tenterà di utilizzare il metodo della sottoclasse il cui nome è cotruito dal'unione della parola "delete" + il nome dell'azione con la prima lettera maiuscola: es: "deleteConfig". la superclasse passerà sempre un timestamp per individuare l'azione specifica

- Implementato il metodo "deleteConfig" della classe Hielen2.ext.source_PhotoMonitoring

- Corretto bug minore di gestione delle azioni in caso esse producano errori non preventivati.


### **22 Gennaio 2021**
- Ristrutturata la pagina di [TODO](http://development.imgback.com/docs/hielen2/TODO/), inserita categorizzazione e valutazione delle tempistica delle attività

### **20 Gennaio 2021**

- modulo `hielen2.ext.source_PhotoMonitoring`:

    rimodellato sulla base del modulo `hielen2.source`.

	definite le classi schema per le azioni:
    
		## action 'config' (Completamente Funzionante)

		class ConfigSchema(ActionSchema):
			master_image = LocalFile(required=True, allow_none=False)
			step_size = fields.Str(required=False, default="8")
			window_size_change = fields.Str(required=False,default="0")
			geo_reference_file = LocalFile(required=False,default=None)
			crs=fields.Str(required=False,default=None)

		## action 'feed'

		class FeedSchema(ActionSchema):
			reference_time = fields.Str(required=False, allow_none=False)
			NS_displacement = LocalFile(required=False, allow_none=False)
			EW_displacement = LocalFile(required=False, allow_none=False)
			Coer = LocalFile(required=False, allow_none=False)


### **18 Gennaio 2021**

Revisione concettuale delle API e modifiche:

- **GET /parametes**: lo schema di ritorno è il seguente (semplicemente _"param"_ al posto di _"name"_):


        {    ...,
             "data": {
                "ARCCE01": [
                    {
                        "series": "ARCCE01_Rotazione_X",
                        "param": "Rotazione X",
                        "unit": "mm/m"},
                       .....
                    }
                ]
        }


- **actionSchemata** è l'api che fornirà gli schemi per le azioni e va a sostituire quella che era "prototypes". Questa esiste ancora e mantiene il legame tra prototipo e modulo ma più che altro le informazioni che stanno nella relativa tabella mi servono per il back-end

       
    GET ../actionschemata[/{prototypes}[/{actions}]]


- **action** come prima, è l'api che gestisce le azioni:

    La versione `POST` nella sostanza non è cambiata a parte il fatto che un'azione dichiarerà sempre un timestamp per default. Ma questa cosa al front-end non interessa dal momento che le info le recupera da actionSchemanta. E' invece importante nella scrittura dei plugin perché in questo modo le azioni possono essere gestite temporalmente.

    La versione `GET`, invece cambia sostanzialmente: non fornirà più i default per la post MA potrà fornire una serie temporale di azioni associate a dei valori di elaborazione che danno informazioni all'utente. in questo formato:

    
	GET ../actions[/{feature}[/{action}]]

ritorna:

    [ { "timestamp":....,"value":.... }, { "timestamp":...., "value":.... }, .... ]

esempio:

    GET ../actions/featurecode/config


	{
		"meta": {
			"response": "ok",
			"message": "",
			"data_type": "GET /actions/ciaociaociao4/config"
		},
		"data": [
			[
				{
					"timestamp": "2020-12-30 01:00:05",
					"value": {
						"master_image": "TIFF image data, little-endian, direntries=14, height=1842, bps=16, compression=none, PhotometricIntepretation=BlackIsZero, width=3545",
						"step_size": "35",
						"window_size_change": "10",
						"transform": [
							15.0,
							0.0,
							464947.5,
							0.0,
							-15.0,
							7977067.5
						],
						"cache": "20201230010005",
						"crs": null
					}
				},
				{
					"timestamp": "2020-12-30 01:00:07",
					"value": {
						"master_image": "TIFF image data, little-endian, direntries=16, height=1842, bps=16, compression=none, PhotometricIntepretation=BlackIsZero, width=3545",
						"timestamp": "2020-12-30 01:00:07",
						"step_size": "35",
						"window_size_change": "10",
						"transform": [
							15.0,
							0.0,
							464947.5,
							0.0,
							-15.0,
							7977067.5
						],
						"cache": "20201230010007",
						"crs": "EPSG:32622"
					}
				}
			]
		]
	}
    
### **15 Gennaio 2021**
- modulo `hielene2.source`: 

    Implementato il metodo `sourceFactory` per la generazione degli ogetti `HeielenSource` in base ai prototipi che sfrutta il cariacmanto dinamico dei moduli specifici (metodo `loadModule`)

    Implementati i metodi e le classi per la gestione agnostica delle azioni ed il recupero degli schemi: `getActionSchema`, `moduleAction`, `HielenSource.execAction`, `HielenSource.getActionValues`

    Implementata la gestione dell'ambiente di cache dedicato alle singole istanze di HielenSource: `HielenSource.makeCachePath`, `HielenSource.getRelativePath`

    Definita la classe primitiva per i modelli di schema per le azioni che impone la definizione della marcatura temporale:

         
         class ActionSchema(Schema):
            timestamp = fields.Str(required=True, allow_none=False)


### **13 Gennaio 2021**
- rimodellato il db: dalla tabella "features" sono state eliminate le colonne "a priori" delle azioni. Queste ultime sono state inserite in una nuova tabella "actions" con chiave multipla ("feature","action","timestamp"). 
- Rivista l'interfaccia db per permettere l'interrogazione su chiave multipla

### **10 Gennaio 2021**
- Progettazione della gestione temporale delle azioni e separazione del concetto di form da quello di risultato della azione: ogni **azione** ha uno **schema di input** e dei **risultati in output** con uno schema **non necessariamente** coincidente. Quello che viene fornito alle form sono i dati necessari ad intraprendere un'azione. I risultati dell'azione devono essere registrati con una marcatura temporale. In questo modo ogni azione è univocamente determinata e gestibile con un modello del tipo ("feature","action","timestamp"), con una cardinalità 1-a-molti tra features e azioni 

- Portata a termine la migrazione della gestione delle azioni che vengono ora completamente affidate ai singoli moduli. L'iterfaccia di alto livello è ora in grado di gestire agonsticamente le chiamate ad azioni arbitrarie purchè ben definite all'interno dei moduli. In questo modo cade il vincolo di definizione do azione "a priori" 

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


