#!/usr/bin/env python
# coding=utf-8
from hielen3.feature import HFeature
import pandas as pd
a=HFeature.retrive('BP')
a.parameters.__demand__()
a=a.parameters.parameters
a=pd.DataFrame(a.items()).set_index(0).squeeze().apply(lambda x: x.check(cache='new')).apply(pd.DataFrame.reset_index).apply(pd.DataFrame.squeeze)

