# coding: utf-8
from hielen3 import db
import pandas as pd
l={ k:w for k,w in a.generator.__dict__['operands'].items() if "__GROUPMAP__" in k }
ll={ k:w.data(cache='new') for k,w in l.items() }
u=pd.concat(ll)
u.index=u.index.swaplevel()
u.unstack()
u.columns=u.columns.map(lambda x: int(x.split('__')[2]))
