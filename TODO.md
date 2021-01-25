
__Nota__: I tempi dichiarati sono da intendersi come di "effettivo lavoro", sono indicativi e potrebbero variare in base agli sviluppi (in particolare del del Modulo Principale). Inoltre i tempi riguradano esclusivamente lo sviluppo di Back-End. Anche se lo sviluppo di Front-End può essere portato avanti parallelamente, sarà necessario tenere adeguatamente in considerazione i realitivi tempi.

## MODULO PRICIPALE:

### astrazione setup di **configurazione**:
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
1    | 2        | bassa     | bassa | Features Prototypes o Interfaccia di modulo: Integrare informazioni capability: [series,map,cloud] e cachable (non sempre è vantaggioso usare la cache)
2    | 2        | media     | media | Mapserver: istanza mapserver con workers (vedi Ecoplame) per la gestione delle mappe statiche tassellate (chiamate wms standard)
xx    | -        | bassa     | **Completo**  | inserire "suggerimenti" nei prototipi delle azioni da passare nella nella risposta alla chiamata "/actionSchemata"
xx    | -        | bassa    | alta | Completare la Progettazione/Implementazione per la generazione delle istanze delle serie dati associate alla feature sulla base dei prototipi. _Non essenziale per Nhazca_
xx    | -        | bassa | **Completo** | API: DELETE `/action/{feature}/{config}`

### astrazione interrogazione **series**:
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
1    | 2        | bassa     | alta | Integrazione dell'interrogazione basata su GeoJeson nell'API 
4    | 4        | bassa     | media | Revisoni minori del modello di astrazione e API
xx   | -        | alta      | bassa  | Impelementare nuovo modulo cache dati. Attualmente è un mero json che per questioni di performance non è possiblie utilizzare in produzione. _Non è essenziale per Nhazca_

### astrazione interrogazione **mappa**
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
4  | 1        | bassa     | bassa | Implementazione modello di astrazione e API per moduli con capability "mappa": Un metodo astratto di hielene.Source che possa essere richiamato dal layer di astrazione e che fornisca in uscita un'immagine georiferita da inserie un path ben codificato. Contestualmente viene prodotto un mapfile associato da passare a mapserver al momento dell'interrogazione (Integrare nel sistema lo sviluppo di SM)
6  | 2        | media     | bassa | Implementazione di modulo di middelware per gestire la produzione/ cacheing delle immagini e passare le chiamate a mapserver per la tassellazione.
    
### astrazione interrogazione **cloud**
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
4 | 4 | bassa | media | Implementazione API di interrogazione cloud: Attualmente il "prodotto" atteso è una pagina html generata in automatico da fornire in front-end.
7 | 3 | media | media | Potree: installazione e gestione del software, Implementazione modulo wrapper (Integrare nel sistema lo sviluppo di GC)


## MODULO ESTESO hielen2.ext.source_PhotoMonitoring
### azione **config**:
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
xx | - | media | **Completo** | Attività di configurazione e persistenza dati

### azione **feed**:
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
2 | 1 | bassa | alta | Aggancio del codice già implementato come prototipo per Tisma + revisione

### interrogazione **dati**
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
2 | 1 | bassa | alta  | Agganco del codice già implementato come prototipo per Tisma
4 | 3 | media | media | Estrazione dati su interpolazione areale

### interrogazione **mappa**
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
3 | 1 | media | alta | Agganco del codice già implementato come prototipo per Tisma + revisione 

## MODULO ESTESO hielen2.ext.source_TinSAR
### azione **config**:
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
5 | 3 | media | media | Analisi info master cloud, strutture di persistenza (verificare matrici sparse), potree run (Integrare sviluppo GC)
1 | 3 | bassa | alta  | Salvataggio delle info sul modello di source_PhotoMonitoring

### azione **feed**: 
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
2 | 4 | media | alta  |  Analisi file in ingresso ed elaborazione file in ingresso (parzialmente implementato)
3 | 4 | media | media |  Aggiornamento strutture di persistenza

### interrogazione **series**
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
3 | 5 | media | bassa | Interazione tramite modello di astrazione (interrogazione tramite GeoJeson mutuabile da source_Photomonitoring). _Nota_: Estrazione puntuale del front-end parzialmente implementata (Integrare sviluppo GC + DD). Estendere con estrazione punti in area e volume (Potree ritorna sempre un set di punti)

### interrogazione **mappa**
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
xx | - | alta | bassa | Proiezione della nuvola su piano x,y: Da trovare un modello efficiente di proiezione. Una volta proiettata l'immagine il resto rientra nel modello generale. 

### interrogazione **cloud**
Giorni/Uomo effettivi | Priorità | Complessità | Copertura | Attività
--------------------- | -------- | ----------- | --------- | -----------
6 | 5 | media | media | Restituire in output il prodotto "html" della nuvola di punti. _Nota_: Produzione html parzialmente implementato da sviluppo di GC.

## ALTRO SENZA PRIORITA'
- **Moduli HielenSource**: attualmente, per comodità, vengono sviluppati come sotto moduli di hielen2 ma il modo corretto è quello di separare lo sviluppo. Sarà sempre possibile farlo dal momento che le strutture vengono sviluppate con l'obiettivo della separazione.
- Implementare procedura di testing delle api
- verificare il default dei campi marshmallow (sembra non prenderlo in considerazione, prob non arriva null ma "")
- POST `/prototypes`
- Migliorare l'output dei doc del JsonValidable
- Gestire i filed Nested nei doc del JsonValidable

