#HIELEN

##Prototipazione degli elementi

###prototypes Api dedicata alle tipologie di elementi e alle azioni (di
input) specifiche. Le azioni sono statiche, nel senso che devono essere
approntate in modo programmatico. Attualmente sono:

::

   config
   feed

Ciò che è dinaminco è il modo in cui le singole tipologie implementano
queste azioni. Questa api serve a conoscere i campi da presentare in
front-end all’utente per comporre la maschera di azione.

::

   POST {uri}/prototypes
   GET  {uri}/prototypes
   GET  {uri}/prototypes/{type}
   GET  {uri}/prototypes/{type}/forms
   GET  {uri}/prototypes/{type}/forms/{form}

tutte le UI create in questo modo saranno aperte su uno specifico
elemento del sistema il cui codice è noto. Il submit della form invierà
le informazioni ad una url di questo genere:

::

   {uri}/actions/{el}/{action}

con un mimetype di tipo **multipart/form-data**

##Manipolazione elenco elementi

###elements Api dedicata agli elementi del sistema: il succo della
faccenda.

Considerazione: gli elementi sono oggetti che producono “elaborazioni”
nel tempo con un caratteristico grado dimensionale (dato, mappe,
nuvole). E’ sempre possibile “proiettare” una “elaborazione” con grado
maggiore su una di grado inferiore. Così da una nuvola può generare
mappe e dalla nuvola o dalle mappe possono essere estratte delle serie
storiche.

**nota 1**: Nelle api di input/output non viene mai specificato il tipo
dell’elemento. Questo perchè: 1. Ad ogni elemento DEVE corrispondere Uno
ed Un solo tipo. Questa non è una restrizione troppo forzata perchè è
sempre possibile definiere elementi nuovi spazialmente coincidenti. 2.
Per il motivo precedente il back-end è sempre in grado di recuperare il
tipo dell’elemento.

**nota 2**: La “mappa degli strumenti” può essere considerata essa
stessa un elemento di tipo mappa…

::

   POST {uri}/elements/
   GET {uri}/elements/
   GET {uri}/elements/{el}
   DELETE {uri}/elements/{el}
   PUT {uri}/elements/{el}

##Interrogazione elementi: operazioni di output L’interrogazione può
riguardare più di un elemento contemporaneamente ed è rivolta in questo
modo:

::

   sitema --> utente

Per questo motivo la struttura della richiesta prevede di specificare
prima l’azione ( *base*, *timeline*, *series*, *map*, *cloud* ) e poi
eventualmente l’elemento.

**nota 1**: non tutte queste api saranno disponibili per tutti gli
elementi. Per ogni elemento sarà noto l’elenco a disposizone tramite
backend (presumibilemnte attraverso GET {uri}/elements/[{el}])

###series

::

   GET {uri}/series
   GET {uri}/series/{el}
   GET {uri}/series/{el}/{param}

###bases

::

   GET {uri}/bases
   GET {uri}/bases/{el}

###timelines

::

   GET {uri}/timelines
   GET {uri}/timelines/{el}

###maps

::

   GET {uri}/maps/[/z/x/y]
   GET {uri}/maps/{el}/[z/x/y]

###clouds

::

   GET {uri}/clouds
   GET {uri}/clouds/{el}

##Azioni sugli elementi: operazioni di input In questo caso le azioni
servono a modificare lo stato di un elemento:

::

   sistema <-- utente

la richiesta viene composta specificando necessariamente l’elemento
prima dell’azione.

**nota 1**: queste trovano riscontro nell’endpoint forms dell’api
prototypes.

###actions Le due azioni attualemente previste sono:

*config*

::

   POST {uri}/actions/{el}/config
   GET {uri}/actions/{el}/config
   PUT {uri}/actions/{el}/config

*feed*

::

   POST {uri}/actions/{el}/feed
   GET {uri}/actions/{el}/feed
   PUT {uri}/actions/{el}/feed/{time}
                                 
