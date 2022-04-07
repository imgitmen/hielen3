## MODULO PRICIPALE:

### astrazione setup di **configurazione**:
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
x        | bassa     | **Completo** | Features Prototypes o Interfaccia di modulo: Integrare informazioni capability: [series,map,cloud] e cachable (non sempre è vantaggioso usare la cache)
x | alta | **Completo** | Revisione dell'ambiente di produzione e accenzione delle istanze.
x        | media     | **Completo** | Mapserver: istanza mapserver con workers (vedi Ecoplame) per la gestione delle mappe statiche tassellate (chiamate wms standard)
x        | bassa     | **Completo**  | inserire "suggerimenti" nei prototipi delle azioni da passare nella nella risposta alla chiamata "/actionSchemata"
x        | bassa | **Completo** | API: DELETE `/action/{feature}/{config}`
2 | alta | **Completo** | Revisione del modello di Source con sottoclassi source->data->map->cloud: Ogni sottoclasse estende le funzionalità in modo da avere livlli di capabilities gerarchici ("cloud" ⊃  "map" ⊃  "data"). Di fatto si può intendere ogni tipologia di elaborazione come timeseries la cui produzione è legata alla specifica capability della tipologia di sorgente (es: le mappe elaborate del parametro "displacement" di una specifica feature da una certa data ad un'altra ).
2        | media    | **Completo** | Completare la Progettazione/Implementazione per la generazione delle istanze delle serie dati associate alla feature sulla base dei prototipi. Da gestire in modo omegeneo le info accessorie generate ad esepio dalle configurazioni.
x        | alta      | **Completo**  | Impelementazione del modulo astratto datacache. Necessario per lo storing delle serie dati. Attualmente implementato con jsson e csv su flesystem. Potrà essere implementato con Redis.
x | media | **Completo** | Gestione del colorrange di riferimento per ogni possibile parametro.


## gestione delle serie dati ##
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
x | media | **Completo** | Rivedere il modello di interrogazione omogeneo per data, maps, cloud: inserire la gestione degli slice temporali, Integrazione dell'interrogazione basata su GeoJeson nell'API
x | alta | media | Intergrazione dei modelli di calcolo estempranei

## gestione delle immagini generate ##
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
x | alta | alta | **Completo** | introduzoine del path "map" e gestione nel sitema, questo path vine esposto per mapserver
x | alta | bassa | **Completo** | gestione di mapserver come fast-cgi

### astrazione interrogazione **data**:
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
2        | bassa     | **Completo** | convergere al modello omgeneo 
1        | media | **Completo** | implementazione della sottoclasse data di source. hielen2.source.Data(hielen2.source.Source)

### astrazione interrogazione **mappa**
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
1        | bassa     | **Completo** | convergere al modello omgeneo 
1        | bassa     | **Completo** | Implementazione modello di astrazione e API per moduli con capability "mappa": classe estesa di source: hielen2.source.Map(hielen2.source.Data) possa essere richiamato dal layer di astrazione e che fornisca in uscita un'immagine georiferita da inserie un path ben codificato. Contestualmente viene prodotto un mapfile associato da passare a mapserver al momento dell'interrogazione (Integrato SM)
    
### astrazione interrogazione **cloud**
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
x        | alta     | **Completo** | convergere al modello omgeneo 
4 | bassa | **Completo** | Implementazione API di interrogazione cloud.
3 | media | **Completo** | Potree: installazione e gestione del software, Implementazione modulo wrapper (Integrare nel sistema lo sviluppo di GC)


## MODULO ESTESO hielen2.ext.source_PhotoMonitoring
### azione **config**:
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
x | media | **Completo** | Attività di configurazione e persistenza dati
x | alta | **Completo** | gestione delle immagini (crs, formati, salvataggi, indicizzazione)

### azione **feed**:
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
x | bassa | **Completo** | Aggancio del codice già implementato come prototipo per Tisma + revisione

### interrogazione **dati**
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
1 | bassa | **Completo**  | Aggancio del codice già implementato come prototipo per Tisma
3 | media | **Completo** | Estrazione dati su interpolazione areale (interrogazione su bounding box)

### interrogazione **mappa**
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
1 | media | **Completo** | Agganco del codice già implementato come prototipo per Tisma + revisione
2 | bassa | **Completo** | associare colorrange in uscita 

## MODULO ESTESO hielen2.ext.source_TinSAR
### azione **config**:
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
3 | media | **Completo** | Analisi info master cloud, strutture di persistenza (verificare matrici sparse), potree run (Integrare sviluppo GC)
3 | bassa | **Completo**  | Salvataggio delle info sul modello di source_PhotoMonitoring

### azione **feed**: 
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
4 | media | **Completo**  |  Analisi file in ingresso ed elaborazione file in ingresso
4 | media | **Completo** |  Aggiornamento strutture di persistenza

### interrogazione **series**
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
5 | media | **Completo** | Interazione tramite modello di astrazione (interrogazione tramite GeoJeson mutuabile da source_Photomonitoring). _Nota_: Estrazione puntuale del front-end parzialmente implementata (Integrare sviluppo GC + DD). Estendere con estrazione punti in area e volume (Potree ritorna sempre un set di punti)

### interrogazione **mappa**
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
x | alta | **Completo** | Proiezione della nuvola su piano x,y: Da trovare un modello efficiente di proiezione. Una volta proiettata l'immagine il resto rientra nel modello generale. 

### interrogazione **cloud**
Priorità | Complessità | Copertura | Attività
-------- | ----------- | --------- | -----------
4 | 5 | media | **Completo** | Restituire in output il prodotto "html" della nuvola di punti. _Nota_: Produzione html parzialmente implementato da sviluppo di GC.

## ALTRO SENZA PRIORITA'
- Gestione degli schemi del db: Definendo gli schemi Marshmallow per le tabelle dei DB è possibile utilizzare Dump e Load per aggirare la non seriabilità di datetime
- **Moduli HielenSource**: attualmente, per comodità, vengono sviluppati come sotto moduli di hielen2 ma il modo corretto è quello di separare lo sviluppo. Sarà sempre possibile farlo dal momento che le strutture vengono sviluppate con l'obiettivo della separazione.
- Implementare procedura di testing delle api
- verificare il default dei campi marshmallow (sembra non prenderlo in considerazione, prob non arriva null ma "")
- POST `/prototypes`
- Migliorare l'output dei doc del JsonValidable
- Gestire i filed Nested nei doc del JsonValidable

