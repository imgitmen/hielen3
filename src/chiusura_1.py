# coding: utf-8
from hielen3 import db
        
def clean_input(inp):
 
    if isinstance(inp,str): inp=inp.split(",")
 
    if not isinstance(inp,(list,set,tuple)) and inp is not None:
        inp=[inp]
 
    if not inp is None: inp = [ a for a in inp if a is not None and a.__len__()]
    if not inp is None and not inp.__len__(): inp = None
 
    return inp
    
        
def chiusura(key=None):
    
    key=clean_input(key) 
    if key is None:
        return []  
    
    oldkey=[]

    while key.__len__() > oldkey.__len__():
        oldkey=key.copy()
        newkey=db['context_context'][{"ancestor":key}]
        filtro=newkey['homogeneous'].astype(bool)
        newkey=list(newkey[filtro]["descendant"])
        key=set([*key,*newkey])
    
    return key
        
