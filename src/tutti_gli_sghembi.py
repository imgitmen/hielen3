# coding: utf-8
from hielen3.feature import HFeature
    
def setcose(n,b,SS):
    A1,A2= b + str(n).rjust(2,"0"), b + str(n+1).rjust(2,"0")
    SS.parameters[f'sgembo {A2} su {A1}']=HFeature.retrive(f'{A2}').parameters[f'sghembo su {A1}']
    
    
def faitutto(m,b):
    SS=HFeature.retrive(f'B{b}')
    for r in range(1,m):
        setcose(r,b,SS)
        
    
faitutto(10,"P")
faitutto(10,"D")
