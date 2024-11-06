# coding: utf-8
from hielen3 import db
from hielen3.utils import clean_input        

def roots_info(contexts=None):

    contexts=clean_input(contexts)
    contexts=db['context'][contexts]
    
    descendants=db['context_context'][:][["homogeneous"]].reset_index('ancestor').sort_index()

    result=contexts.join(descendants,how='left')
    result=result[~result['homogeneous'].notna()]
    result["descendants_count"]=result["ID"].apply(lambda x: lineages(x).__len__())
    result=result.drop(["ancestor","homogeneous"],axis=1)
    result.columns=["context","label","description","descendants_count"]

    return result


def lineages(key=None, level=None):
    
    key=clean_input(key)

    if key is None:
        raise ValueError ("key must not be None")  
    
    oldkey=[]

    while key.__len__() > oldkey.__len__() and (level is None or level >= 0):
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

    while key.__len__() > oldkey.__len__() and (level is None or level >= 0):
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
 

