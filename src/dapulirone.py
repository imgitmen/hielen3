# coding: utf-8
import pandas as pd
from numpy import nan
from hielen3.api_split_context import contexts as ct
from hielen3 import contextmanager as cm
dipendenti=pd.read_csv("giorgio",sep=";",header=None,index_col=0).replace(nan,"")
    
for d in dipendenti.index:
    l=cm.ancestors(key=d,homo_only=False)
    l.sort()
    print (d,l)
    
