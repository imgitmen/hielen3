# coding: utf-8
from hielen3 import db
db
db["61a5f984992fb"][["9816f4ff-0b24-4098-b05d-1382500843ff","999a1b59-f54e-44d8-8324-aa234698a583"],slice("2024-03-23 01:00:00","2024-05-03 19:00:00")]
db["datacache"][["9816f4ff-0b24-4098-b05d-1382500843ff","999a1b59-f54e-44d8-8324-aa234698a583"],slice("2024-03-23 01:00:00","2024-05-03 19:00:00")]
db["datacache"][["9816f4ff-0b24-4098-b05d-1382500843ff","999a1b59-f54e-44d8-8324-aa234698a583"],slice("2024-03-23 01:00:00","2024-05-03 19:00:00")].index.stats
u=db["datacache"][["9816f4ff-0b24-4098-b05d-1382500843ff","999a1b59-f54e-44d8-8324-aa234698a583"],slice("2024-03-23 01:00:00","2024-05-03 19:00:00")].index
u.to_series()
uu=u.to_series()
uu.struct
uu.describe
uu.describe()
uu.describe
uu.describe()
uu.describe(include='all')
#uu.describe(include='all')
db["series"][:]
db["series"][:]["datable"]
db["series"][:]["datatable"]
db["series"][:]["datatable"].reset_index()
db["series"][:]["datatable"].reset_index().set_index("datatable")
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable")
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").asstring
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: dict(x))
#db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: dict(x)).apply()
import pd
import pandas as pd
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: Series(dict(x))).apply()
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: pd.Series(dict(x))).apply()
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: dict(x)).apply(pd.Series)
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: dict(x)["uuid"])
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: dict(x))
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: list(x))
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: dict(x["uuid"]))
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: list(x["uuid"]))
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: list(x["uuid"])).reset_index()
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: list(x["uuid"])).reset_index().apply(lambda x: db[datatable][0].index.to_series.describe)
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: list(x["uuid"])).reset_index().apply(lambda x: db[x[datatable]][x[0]].index.to_series.describe)
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: list(x["uuid"])).reset_index().apply(lambda x: db[x["datatable"]][x[0]].index.to_series.describe)
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: list(x["uuid"])).reset_index().apply(lambda x: db[x["datatable"]][x[0]].index.to_series.describe,axis=1)
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: list(x["uuid"])).reset_index().apply(lambda x: db[x["datatable"]][x[0]].index.to_series().describe,axis=1)
db["series"][:]["datatable"].reset_index()
db["series"][:]["datatable"].reset_index()db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable")
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable")
db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: list(x["uuid"]))
aa=db["series"][:]["datatable"].reset_index().set_index("datatable").groupby("datatable").apply(lambda x: list(x["uuid"]))
