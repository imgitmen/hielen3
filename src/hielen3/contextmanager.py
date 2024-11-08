# coding: utf-8
from hielen3 import db
from hielen3.utils import clean_input
from pandas import DataFrame

def roots_info(contexts=None):

    contexts=clean_input(contexts)
    try:
        contexts=db['context'][contexts]
    except KeyError as e:
        return DataFrame()
   
    try:
        descendants=db['context_context'][:][["homogeneous"]].reset_index('ancestor').sort_index()
    except KeyError as e:
        contexts["descendants_count"] = 0
        contexts.columns=["context","label","description","descendants_count"]
        return contexts

    result=contexts.join(descendants['ancestor'],how='left')
    result=result[result['ancestor'].isna()]
    result["descendants_count"]=result["ID"].apply(lambda x: lineages(x,homo_only=False).__len__() - 1)
    result=result.drop(["ancestor"],axis=1)
    result.columns=["context","label","description","descendants_count"]

    return result


def lineages(key=None, level=None, homo_only=True):
    
    key=clean_input(key)

    if key is None:
        raise ValueError ("key must not be None")  
    
    oldkey=[]

    while key.__len__() > oldkey.__len__() and (level is None or level >= 0):
        oldkey=key.copy()
        try:
            newkey=db['context_context'][{"ancestor":key}]
            if homo_only:
                fltr=newkey['homogeneous'].astype(bool)
                newkey=newkey[fltr]
            newkey=list(newkey["descendant"])
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
 

