## Con Priorità


### **v2.0.6** Interfacce delle Informazioni con risposta mockup. Intento: agganciare lavoro Daniele

- GET `/bases`
- GET `/bases/{feature}`
- GET `/timelines`
- GET `/timelines/{feature}`
- GET `/data/` estensione del modello di datamap per accettare GeoGeson

### **v2.0.7** Rivistazione del modulo PhotMonitoring come "source". Intento: agganciare le serie dati prodotte dall'elaborazione Photmonitoring alle interfacce

### **v2.0.8** Implementazione del modulo TinSar come "source". Intento: agganciare le serie dati prodotte dall'elaborazione TinSar alle interfacce

### **v2.0.9** Implementazione delle chiamate di mappa

- GET `/maps/[/z/x/y]`
- GET `/maps/{feature}/[z/x/y]`

### **v2.0.10** Implemntazione chiamate cloud

- GET `/cloud/{feature}`

## Senza priorità
- Obiettivo: assegnare una timestamp ad ogni informazione: le properties degli ogetti dovranno essere delle serie dati. Concetto di informazione minima.
- Implementare procedura di testing delle api
- verificare il default dei campi marshmallow (sembra non prenderlo in considerazione, prob non arriva null ma "")
- POST `/prototypes`
- Migliorare l'output dei doc del JsonValidable
- Gestire i filed Nested nei doc del JsonValidable

