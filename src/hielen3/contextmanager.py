# coding: utf-8
from hielen3 import db
from hielen3.utils import clean_input
from hielen3.utils import uuid
from pandas import DataFrame
from numpy import nan
from json import dumps
from anytree import Node, RenderTree

def roots_info(contexts=None, homo_only=True):

    """
        ritorna tutti i contesti root (senza genitore) con il conteggio
        dei contesti omogenei e non discendenti di quella root
    """

    # filtriamo i contesti che esistono
    contexts=clean_input(contexts)
    try:
        contexts=db['context'][ancestors(contexts,homo_only=homo_only)]
    except KeyError as e:
        return DataFrame()
   
    try:
        descendants=db['context_context'][:][['homogeneous']].reset_index('ancestor').sort_index()
    except KeyError as e:
        contexts['descendants_count'] = 0
        contexts.columns=['context','label','description','descendants_count']
        return contexts

    result=contexts.join(descendants[['ancestor','homogeneous']],how='left')

    
    result['roots']=result['homogeneous'].replace(nan,0)

    if homo_only:
        result=result[~result['roots'].astype('bool')]
    else:
        result=result[result['ancestor'].isna()]

    result['descendants_count']=result['ID'].apply(lambda x: lineages(x,homo_only=homo_only).__len__() - 1)
    result=result.drop(['ancestor','homogeneous','roots'],axis=1)
    result.columns=['context','label','description','descendants_count']

    return result


def lineages(key=None, level=None, homo_only=True):

    """
        ritorna l'insieme dei contesti apparteneti alla discendenza 
        del contesto in input.
    """
    
    key=clean_input(key)

    if key is None:
        raise ValueError ("key must not be None")  
    
    oldkey=[]

    while key.__len__() > oldkey.__len__() and (level is None or level >= 0):
        oldkey=key.copy()
        try:
            newkey=db['context_context'][{'ancestor':key}]
            if homo_only:
                fltr=newkey['homogeneous'].astype(bool)
                newkey=newkey[fltr]
            newkey=list(newkey['descendant'])
        except KeyError as e:
            newkey=oldkey

        key=set([*key,*newkey])

        if level is not None: level -= 1

    if key.__len__():
        key = list(db["context"][key].index)
    
    return key


def ancestors(key=None, level=None, homo_only=True):
    
    """
        ritorna la linea di discendenza salendo dal contesto in input
        fino alla radice 
    """

    key=clean_input(key)

    if key is None:
        raise ValueError ("key must not be None")  
    
    oldkey=[]

    while key.__len__() > oldkey.__len__() and (level is None or level >= 0):
        oldkey=key.copy()
        try:
            newkey=db['context_context'][{"descendant":key}]
            if homo_only:
                fltr=newkey['homogeneous'].astype(bool)
                newkey=newkey[fltr]
            newkey=list(newkey["ancestor"])
            #fltr=newkey['homogeneous'].astype(bool)
            #newkey=list(newkey[fltr]["descendant"])
        except KeyError as e:
            newkey=oldkey

        key=set([*key,*newkey])

        if level is not None: level -= 1

    if key.__len__():
        key = list(db["context"][key].index)
    
    return key
 

def family(contexts=None, homo_only=True):

    """
        ritorna la famiglia del contesto
    """

    # tutto il ramo genealogico dall'elemento in input fino alla radice
    ancestors_list=ancestors(contexts,homo_only=homo_only)
    # solo le radici degli alberi precedenti
    roots_list=list(roots_info(ancestors_list).index)
    # tutta la discendenza dei roots 
    lineages_list=lineages(roots_list,homo_only=homo_only)

    lineages_info=db["context"][lineages_list]

    try:
        descendants_rel=db["context_context"][lineages_list]
        descendants_rel=descendants_rel[["homogeneous","klass"]].reset_index("ancestor")
    except KeyError as e:
        descendants_rel=DataFrame([],columns=["parent","homogeneous","klass"])

    result = lineages_info.join(descendants_rel).replace(nan,None)
   
    result.columns = ["context","label","description","parent","homogeneous","klass"]
 
    if homo_only:
        result.loc[roots_list,"parent"] = None

    return result


def feature_in_family(feature,contexts=None,homo_only=True):

    """
        in caso di homo_only:     ritorna il contesto in cui sta la feature, omogeneo ai 
                                  contesti in input
        in caso di not homo_only: ritorna tutti i contesti omogenei e non, 
                                  in cui si trova la feature che fanno parte della famiglia
    """
    try:
        fam=list(family(contexts,homo_only=homo_only)["context"].drop_duplicates().values)
        contexts=list(db["context_feature"][{"context":fam,"feature":feature}]["context"].drop_duplicates().values)
    except KeyError:
        # raise e
        return []

    return contexts


def context_in_family(context,contexts,homo_only=True):

    try:
        fam=list(family(contexts,homo_only=homo_only)["context"].drop_duplicates().values)
    except KeyError:
        # raise e
        return False

    return context in fam


def manage_feature_context(feature,target,geometry=None):

    popped_cont_feat = None

    try:
        source=feature_in_family(feature,target,homo_only=True)

        if source.__len__():
            """
            #estrarre il link context_feature
            #modificare il context (pop)
            #inserire la nuova assoxciazione

            """
            popped_cont_feat = db["context_feature"].pop({"context":source[0],"feature":feature}).to_dict(orient="records")[0]
            
            cont_feat = {**popped_cont_feat}
        else:
            cont_feat = {"feature":feature}

        cont_feat["context"]=target
            

        if geometry is not None and geometry.__len__():
            try:
                geouuid=cont_feat["geometry"]
                if geouuid is None:
                    raise KeyError()
            except KeyError as e:
                geouuid=uuid()

            db["geometry"][geouuid]={"geometry":geometry}
            cont_feat["geometry"]=geouuid
        
        db["context_feature"][cont_feat]=cont_feat

    except Exception as e:
        if popped_cont_feat is not None:
            db["context_feature"][popped_cont_feat]=popped_cont_feat
        raise e


def remove_feature_context_geometry(feature,context):

    try:
        cont_feat = db["context_feature"][{"context":context,"feature":feature}].to_dict(orient="records")[0]
        geo_uuid=cont_feat.pop("geometry")
        db["context_feature"][cont_feat] = {"geometry":None}
    except KeyError as e:
        cont_feat = {}

    try:
        popped_geometry=db["geometry"].pop(geo_uuid).to_dict(orient="records")[0]["geometry"]
    except Exception as e:
        popped_geometry={}

    return popped_geometry


def detouch_feature_context(feature,context):

    try:
        popped_cont_feat = db["context_feature"].pop({"context":context,"feature":feature}).to_dict(orient="records")[0]
    except KeyError as e:
        popped_cont_feat = {}

    try:
        popped_cont_feat["geometry"]=remove_feature_context_geometry(feature,context)
    except Exception as e:
        pass

    return popped_cont_feat


def contexts_with_homo_parent(contexts=None):

    out = []

    contexts=clean_input(contexts)
    
    if contexts.__len__() == 0:
        return out

    try:
        dd=db["context_context"][{"descendant":contexts}]
    except KeyError as e:
        return out

    out = list (dd[dd["homogeneous"]==1][["ancestor","descendant"]])

    return out


def features_interfamily_collisions(context,colliders,homo_only=True):

    out = []

    context = clean_input(context)
    colliders = clean_input(colliders)

    if not context.__len__():
        return out

    context=context[0]
    try:
        family_context=list(family(context,homo_only=homo_only)["context"])
    except KeyError as e:
        return out

    try:
        if family_context.__len__() == 0:
            raise KeyError()
        feats_family_context=set(db["features_info_v2"][{"context":[*family_context]}]["feature"])
    except KeyError as e:
        return out

    for collider in colliders:
        try:
            family_collider=list(family(collider,homo_only=homo_only)["context"])
        except KeyError as e:
            continue

        try:
            feats_family_collider=set(db["features_info_v2"][{"context":[*family_collider]}]["feature"])
        except KeyError as e:
            continue

        # intersection
        collisions=feats_family_context & feats_family_collider

        if collisions.__len__() > 0:

            out.append(
                    {
                        "context":context,
                        "collider":collider,
                        "collision":list(collisions)
                        }
                    )


    return out


def print_tree(nodes: dict, roots: set) -> None:
    for root in roots:
        print()
        for pre, _, node in RenderTree(nodes[root]):
            print(f'{pre}{node.name} ({node.val})')


def add_nodes(nodes: dict, roots: set, parent: str, child: str, val: int) -> None:
    if parent not in nodes:
        nodes[parent] = Node(parent, val=None)
        roots.add(parent)
    if child not in nodes:
        nodes[child] = Node(child, val=val)
    else:
        nodes[child].val = val
    nodes[child].parent = nodes[parent]
    if child in roots:
        roots.remove(child)


def create_tree(df: DataFrame) -> None:
    nodes = {}
    roots = set()
    for row in df.itertuples(index=False, name='df_row'):
        if row.c_key is not None:
            add_nodes(nodes, roots, row.p_key, row.c_key, row.val)
    print_tree(nodes, roots)


def print_family(contexts=None, homo_only=True):

    contexts = clean_input(contexts)

    if contexts.__len__() == 0:
        try:
            contexts=list(roots_info()["context"])
        except Exception as e:
            contexts = []
    
    for context in contexts:
        roots=roots_info(context,homo_only=homo_only)
        if not roots.empty:
            roots=roots["context"]

            for root in roots.values:
                f=family(root,homo_only=homo_only)
                f=f.reset_index()[["parent","context","label"]]
                f.columns=["p_key","c_key","val"]
                #f=f[~f["p_key"].isna()]
                create_tree(f)


