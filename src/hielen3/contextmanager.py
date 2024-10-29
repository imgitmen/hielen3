# coding: utf-8
from hielen3 import db
from hielen3.utils import clean_input        
        
def lineages(key=None, level=None):
    
    key=clean_input(key)

    if key is None:
        raise ValueError ("key must not be None")  
    
    oldkey=[]

    while key.__len__() > oldkey.__len__() and (level is None or level):
        oldkey=key.copy()
        try:
            newkey=db['context_context'][{"ancestor":key}]
            fltr=newkey['homogeneous'].astype(bool)
            newkey=list(newkey[fltr]["descendant"])
        except KeyError as e:
            newkey=oldkey

        key=set([*key,*newkey])

        if level is not None: level -= 1

    key = list(db["context"][key].index)
    
    return key
        
def ancestors(key=None, level=None):
    
    key=clean_input(key)

    if key is None:
        raise ValueError ("key must not be None")  
    
    oldkey=[]

    while key.__len__() > oldkey.__len__() and (level is None or level):
        oldkey=key.copy()
        try:
            newkey=db['context_context'][{"descendant":key}]['ancestor']
            #fltr=newkey['homogeneous'].astype(bool)
            #newkey=list(newkey[fltr]["descendant"])
        except KeyError as e:
            newkey=oldkey

        key=set([*key,*newkey])

        if level is not None: level -= 1

    key = list(db["context"][key].index)
    
    return key
 

