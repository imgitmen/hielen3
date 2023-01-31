# coding: utf-8
S1=HSeries('bb8880e3-5820-41f6-9c67-b9d1bae6b5d4')
from hielen3.series import HSeries
S1=HSeries('bb8880e3-5820-41f6-9c67-b9d1bae6b5d4')
S1
S1.data()
d=S1.data()
d.mask(d>0.01,0)
d
a=d.to_frame()
a.join(d)
a.join(d,lsuffix='a_')
c=a.join(d,lsuffix='a_')
c.mask(c>0.01,0)
c.where(c>0.01,0)
from numpy import nan
c=c.where(c>0.01,nan)
c[c.notna().all(axis=1)]
