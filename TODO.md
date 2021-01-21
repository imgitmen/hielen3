## Con Priorità


### MODULO ESTESO hielen2.ext.source_PhotoMonitoring

-   

-   analisi dei file csv in ingresso (NS, EW, Correlation se esiste)
-   aggirnamento di filecache/{uid}/multidim.nc

### Configurazione hielen2.ext.TinSAR

-   analisi della formato della master cloud
-   salvataggio (stoccaggio) della nuvola di base
-   recupero info geografiche
-   in caso non esistano info di proiezione geografica si considera spazio cartesiano con coordinate con adeguate alla nuvola base (da verificare)
-   configurare file netCDF e salvarlo in filecache/{uid}/multidim.nc (dati)
-   definire percorso di salvataggio tiles: filecache/{uid}/{map}/ (tiles mappe)
-   configurare cartella di cache per potree filecache/{uid}/{cloud} (potree)

### Feed hielen2.ext.TinSAR

1. Analisi file in ingresso
2. aggiornamento filecache/{uid}/multidim.nc
3. aggiornamento filecache/{uid}/{cloud}

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

### **v2.0.10** Implementazione chiamate cloud

- GET `/cloud/{feature}`

## Senza priorità

- **Moduli HielenSource**: attualmente, per comodità, vengono sviluppati come sotto moduli di hielen2 ma il modo corretto è quello di separare lo sviluppo. Sarà sempre possibile farlo dal momento che le strutture vengono sviluppate con l'obiettivo della separazione.
- ~~**Moduli HielenSource**: Definire in backend le form come Marshmallow.Schema in modo da condividere la struttura tra moduli e api~~

- Obiettivo: assegnare una timestamp ad ogni informazione: le properties degli ogetti dovranno essere delle serie dati. Concetto di informazione minima.
- Implementare procedura di testing delle api
- verificare il default dei campi marshmallow (sembra non prenderlo in considerazione, prob non arriva null ma "")
- POST `/prototypes`
- Migliorare l'output dei doc del JsonValidable
- Gestire i filed Nested nei doc del JsonValidable

