CHANGELOG
=========
## 2.0.2 November 3 2020
- L'api `../series` diventa `../data` e cambia il suo comportamento: la variabile di tipo json  _datamap_ si aspetta il campo _series_ invece di _parameters_. In questo campo devono essere inseriti i codici delle serie e non più il costrutto "codice_elemento:parametro_elemento". I codici delle serie si possono recuperarare dall'api `../elements` (vedi Nota successiva)
- L'api `../elements` cambia la sua risposta e per ogni parametro nella lista _parameters_ degli elementi viene agiunto il codice della serie di riferimento che può essere fornito senza modifiche a `data`:

        {
            "series":<seriescode>,
            "name":<seriesname>,
            "um":<seriesunit>
        }
