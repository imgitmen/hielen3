# coding: utf-8
from hielen3.feature import HFeature
import numpy as np
import pandas as pd
a=HFeature.retrive('5b1aea1c-66b5-4634-a935-66d65f086c39')
d=a.parameters['sghembo su D01'].data()
ag=pd.DataFrame([['Alarm','lower'],['Warning','lower'],['Warning','upper'],['Alarm','upper']], index=pd.Index([-0.1,-0.05,0.05,0.1],name='value'), columns=['grade','direction']).sort_index()
    
    
if ag['direction'].iloc[0] == 'lower':
    ag=pd.concat([ag,pd.DataFrame([[None,'lower']], index=pd.Index([-np.inf],name='value'), columns=['grade','direction'])]).sort_index()
    
    
if ag['direction'].iloc[-1] == 'upper':
    ag=pd.concat([ag,pd.DataFrame([[None,'upper']], index=pd.Index([np.inf],name='value'), columns=['grade','direction'])]).sort_index()

ag
ag.reset_index()
aa=ag.reset_index()

bb=aa['value'].copy()


aa.loc[aa['direction']=='lower',['value','grade']] = aa.loc[aa['direction']=='lower',['value','grade']].shift(-1)
aa.loc[aa['direction']=='upper',['value','grade']] = aa.loc[aa['direction']=='upper',['value','grade']].shift(1)
aa['limit']=bb

aa=aa[aa['value'].notna()]
aa.index.name='idt'
aa=aa.reset_index()

d=d.to_frame()
v=d.columns[0]

for i in aa.index:
    d.loc[d[v].between(min(aa.loc[i,'value'],aa.loc[i,'limit']), max(aa.loc[i,'value'],aa.loc[i,'limit']), inclusive='neither'),'grade']=aa.loc[i,'idt']
    
     
aa=aa.set_index('idt')
d=d.reset_index().set_index('grade').sort_index()

d=d.join(aa,how='left').set_index('timestamp').sort_index()[[v,'value','direction','grade']]

