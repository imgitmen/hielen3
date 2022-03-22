CHANGELOG
=========
## **v3.0.3**
- modifica api `POST /feature/`: non prende più il parametro **"uid"**. Il campo "uid" della feature viene ora generato dalla chiamata, secondo gli standard di "uuid".
- modifica definizione della classe `hielen3.api.feature.FeaturePropertiesSchema`: rinominato il campo **"context"** in **"milieu"**. Questo coinvolge la chiamata API `POST /feature/` in quanto la classe modificata gestisce e valida il json da passare al parametro `properies` dell'API.
- modifica api `POST,GET,PUT,DELETE /feature/`: rinominato il parametro **"cntxt"** in **"milieu"**. La parola "milieu" al contrario di "context" non dà problemi di interpretazione al sottostante strato di "Hug" (per questo motivo era stata utilizzata "cntxt"). In questo modo vengono uniformati i parmametri di queste API con il campo della classe di gestione delle properties.

