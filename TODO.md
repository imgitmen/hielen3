## Con Priorità

### **v2.0.5** Interfacce delle Azioni con risposta mockup. Intento: agganciare lavoro SimoneD

#### _Struttura principale `/actions/{feature}/{action}`_:

1. ~~accettare content-type/multipart~~
2. ~~recuperare il prototipo di feature e verificare il content~~
3. ~~collegare il parsing dei field del multipart alla form della feature~~
4. ~~Implementare dummy POST generico che risponde in base alla from della feture~~
6. ~~rimodellare features db~~
7. ~~Fornire le form attraverso /features e non attraverso prototype (un passaggio di meno)~~
8. ~~Definire superclasse source~~
9. ~~Inserire modulo di riferimento tra le info del prototipo~~
10. ~~Implemntare passaggio a modulo (loading dinamico come source dei dati)~~

#### _config_:

- POST `/actions/{el}/config`
- GET `/actions/{el}/config`
- PUT `/actions/{el}/config`

#### _feed_:

- POST `/actions/{el}/feed`
- GET `/actions/{el}/feed`
- PUT `/actions/{el}/feed/{time}`


### **v2.0.6** Interfacce delle Informazioni con risposta mockup. Intento: agganciare lavoro Daniele

- GET `/bases`
- GET `/bases/{el}`
- GET `/timelines`
- GET `/timelines/{el}`
- GET `/data/` estensione del modello di datamap per accettare GeoGeson

### **v2.0.7** Rivistazione del modulo PhotMonitoring come "source". Intento: agganciare le serie dati prodotte dall'elaborazione Photmonitoring alle interfacce

### **v2.0.8** Implementazione del modulo TinSar come "source". Intento: agganciare le serie dati prodotte dall'elaborazione TinSar alle interfacce

### **v2.0.9** Implementazione delle chiamate di mappa

- GET `/maps/[/z/x/y]`
- GET `/maps/{el}/[z/x/y]`

### **v2.0.10** Implemntazione chiamate cloud

- GET `/cloud/{el}`

## Senza priorità
- Obiettivo: assegnare una timestamp ad ogni informazione: le properties degli ogetti dovranno essere delle serie dati. Concetto di informazione minima.
- Implementare procedura di testing delle api
- verificare il default dei campi marshmallow (sembra non prenderlo in considerazione, prob non arriva null ma "")
- POST `/prototypes`
- Migliorare l'output dei doc del JsonValidable
- Gestire i filed Nested nei doc del JsonValidable

