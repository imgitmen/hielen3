# coding: utf-8
from hielen3 import db
from hielen3.api.query2 import tabular_data
datamap=[{"series":["3f695c37-aed7-4e7f-a642-1779dfb1eb87","4021c86d-6efe-4ca2-8fbc-0209c8ecfc59"]}]
t=tabular_data('data',datamap=datamap);
h=db['features_parameters_headers'][list(t.columns)]
t1=t.T.join(h).set_index(['feature','parameter','series']).T
t1.index.name='timestamp'
