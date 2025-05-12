# coding: utf-8
from hielen3 import db
from hielen3.utils import clean_input
from hielen3.utils import uuid
from pandas import DataFrame, Series
from numpy import nan
from json import dumps
from anytree import Node, RenderTree


def clean_contexts(contexts=None):

    if contexts is None or (isinstance(contexts,(list,set,tuple)) and contexts.__len__() == 0):
        return contexts

    out = []

    try:
        out = list(db["context"][contexts]["ID"])
    except KeyError as e:
        pass

    return out




def roots_info(contexts=None, homo_only=True):

    """
        ritorna tutti i contesti root (senza genitore) con il conteggio
        dei contesti omogenei e non discendenti di quella root
    """

    # filtriamo i contesti che esistono
    contexts=clean_input(contexts)

    cleaned_contexts=clean_contexts(contexts)

    if cleaned_contexts.__len__() == 0 and contexts.__len__() > 0:
        return DataFrame()

    contexts=db['context'][ancestors(cleaned_contexts,homo_only=homo_only)]
   
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


def contexts_features_visibility(contexts = None, features=None, orphans = True):

    def __expand_contexts_info__(key):

        key = clean_input(key)
        info=db["context"][key].loc[key]
        info["actual"]=False
        info.loc[key[0],"actual"]=True
        info=info.to_dict(orient="records")

        return info

    def __upper_ancestors_limit__(path = None,limit = None):

        limit = clean_input(limit)
        path = clean_input(path)

        if not limit.__len__():
            return path

        top = -1

        for l in limit:
            try:
                top = max(top,min(path.index(l)+1,path.__len__()))
            except Exception as e:
                pass

        return path[:top]

    contexts=clean_input(contexts)

    features=clean_input(features)

    ## Trova tutti i contesti accessibili da quelli in ingresso
    try:
        contexts=lineages(contexts,homo_only=False)
    except KeyError as e:
        pass

    upper_limit = contexts


    AND_clausoles=[]

 
    if features.__len__():
    
        features_clsl = ','.join(map(lambda x: '"' + x + '"', features))

        AND_clausoles.append(f"f.uuid in ({features_clsl})")

   
    if orphans:
        orphans_clsl = "cf.context is NULL"
    else:
        orphans_clsl = "cf.context is not NULL"


    if contexts.__len__():
    
        contexts_clsl = ','.join(map(lambda x: '"' + x + '"', contexts))

        if orphans:

            contexts_clsl = f"({orphans_clsl} OR cf.context in ({contexts_clsl}))"
        else:

            contexts_clsl = f"({orphans_clsl} AND cf.context in ({contexts_clsl}))"

    else:

        contexts_clsl = f"({orphans_clsl})"

    

    AND_clausoles.append(contexts_clsl)

    clausoles=" AND ".join(AND_clausoles)


    claus=""

    if not orphans or contexts.__len__() or features.__len__():
        claus = f" WHERE {clausoles}"

    """
        la query fa selezione puntuale sull'identificativo della 
        feature unito ai contesti di appartenenza in base a questi filtri:

        contexts: feature appartenenti al contesto in input + quelle orfane se orphans = true
        features: feature comprese nell'elenco in input in AND con la condizione di orphans
        
        le condizioni context e features sono in AND

        context e features vuoti non filtrano

    """

    qry=f"""
        select 
            f.uuid,
            f.label,
            cf.context
        from
            feature f
        left join 
            context_feature cf
        on
            f.uuid = cf.feature
        {claus}
    """

    #print (qry)

    ## Seleziona tutte le features associate ai contesti accessibili
    features=db["query"][qry]

    ## Seleziona l'iniseme dei contesti direttamente associati alle feature
    contexts=list(features["context"].astype(str).drop_duplicates().replace("None",None))

    ## Costruisce i cammini da ogni contesto alla rispettiva root
    paths=ancestors_paths(contexts)

    ## taglia i cammini fino ai contexts in input
    paths=paths.apply(lambda x: __upper_ancestors_limit__(x,upper_limit))
    ## Espande le info dei contesti assegnando al primo il flag actual=True
    paths=paths.apply(__expand_contexts_info__)
    paths.name="contexts"

    ## Si associano i cammini alle features: se una feature appare in più cammini
    ## appare più volte nell'inidice. Per costruzione i cammini sono tutti disomogenei
    ## tra di loro
    features["context"] = features["context"].astype(str).replace("None",None)
    res = features.set_index("context").join(paths,how="left").set_index(["uuid","label"]).replace(nan,None)
    
    ## Si raggruppano i diversi cammini per ogni feature
    res = res.groupby(["uuid","label"]).apply(lambda x: clean_input(list(x["contexts"]))).reset_index("label")

    res.columns=["label","contexts"]
    res.index.name="feature"
    res.name="features_paths"
    
    return res


def ancestors_paths(key=None):

    key = clean_input(key)
    paths = Series(key)
    paths.index=paths
    paths=paths.apply(ancestors, homo_only=True)

    return paths


def ancestors(key=None, level=None, homo_only=True):
    
    """
        ritorna la linea di discendenza salendo dal contesto in input
        fino alla radice 


        NOTA: per costruzione, passando un solo contesto e il 
        parametro homo_only a true, viene restiruito il path
        univoco e ordinato che unisce il contesto in input alla root

    """

    key=clean_input(key)
    key=clean_contexts(key)

    out = []

    ## DEVE ESSERE UN ARRAY DI ARRAY!! RICORDATELO!!
    list_level_keys=[key]

    while key.__len__() and (level is None or level >= 0):

        try:
            newkey=db['context_context'][{"descendant":key}].droplevel("descendant")
           
            if homo_only:
                fltr=newkey['homogeneous'].astype(bool)
                newkey=newkey[fltr]

            newkey=newkey[~newkey.index.isin(list_level_keys[-1])]
            
            newkey=list(newkey["ancestor"].drop_duplicates())
            
            list_level_keys.append(newkey)

        except KeyError as e:
            # SERVE PER GESTIRE LA CHIUSURA
            newkey=[]

        key=newkey

        if level is not None: level -= 1

    for k in list_level_keys:
        out=[*out,*k]

    return out
 


def family(contexts=None, homo_only=True):

    """
        ritorna la famiglia del contesto
    """

    # tutto il ramo genealogico dall'elemento in input fino alla radice

    contexts=clean_input(contexts)
    ancestors_list=ancestors(contexts,homo_only=homo_only)

    # se la lista degli ancestors è vuota ma context non lo è
    # vuol dire che sono stati passati solo contesti non validi
    # se la lista dei contesti è invece vuota, vuol dire che vengono
    # richieste tutte le famiglie, senza clausola where
    if ancestors_list.__len__() == 0 and contexts.__len__() > 0:
        return DataFrame()
    
    # solo le radici degli alberi precedenti
    roots_list=list(roots_info(ancestors_list).index)

    #roots_list=list(roots_info(contexts).index)
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

"""
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

"""

