#!/usr/bin/env python
# coding=utf-8
import hug
import falcon
from hielen3 import db
from hielen3.utils import ResponseFormatter
from hielen3.utils import clean_input
from hielen3.utils import boolenize 
from hielen3.contextmanager import lineages
from hielen3.contextmanager import ancestors
from hielen3.contextmanager import family
from hielen3.contextmanager import features_interfamily_collisions
from hielen3.contextmanager import contexts_with_homo_parent
from hielen3.contextmanager import roots_info

#GET

@hug.get("/")
def get_context_param(
    cntxt=None,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
    out = ResponseFormatter(status=falcon.HTTP_OK)

    cntxt=clean_input(cntxt)

    try:
        out.data=db["context"][cntxt].to_dict(orient="records")
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return

@hug.get("/{cntxt}")
def get_context_endpoint(
    cntxt=None,
    request=None,
    response=None,
    **kwargs
):

    return get_context_param(cntxt,request,response,**kwargs)



# POST

@hug.post("/")
def create_context_param(
    cntxt,
    label=None,
    description=None,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
    out = ResponseFormatter(status=falcon.HTTP_CREATED)

    cntxt=clean_input(cntxt)
    description = clean_input(description,trim_none=False)
    label = clean_input(label,trim_none=False)
    
    try:
        if not cntxt.__len__():
            raise Exception ( "cntxt required" )

        if description.__len__() > 1 and description.__len__() != cntxt.__len__():
            raise ValueError ("description length invalid")

        if label.__len__() > 1 and label.__len__() != cntxt.__len__():
            raise ValueError ("label length invalid")


        if description.__len__() == 1:
            v = description[0]
            description=[ v for a in cntxt ]

        if label.__len__() == 1:
            v = label[0]
            label=[ v for a in cntxt ]
  
        for i in range(0,cntxt.__len__()):
            db["context"][cntxt[i]]={"label":label[i],"description":description[i]}

    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return


@hug.post("/{cntxt}")
def create_context_endpoint(
      cntxt,
      label=None,
      description=None,
      request=None,
      response=None,
      **kwargs
):
    return create_context_param(cntxt=cntxt,label=label,description=description,request=request,response=response,**kwargs)


@hug.delete("/")
def delete_context_param(
    cntxt,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
    out = ResponseFormatter(status=falcon.HTTP_OK)

    cntxt=clean_input(cntxt)

    try:
        try:
            # Verifico che non sia padre di nessuno
            db["context_context"][{"ancestor":cntxt}]
            raise ValueError(f"Context {cntxt} has descendants. Can't drop.")
        except KeyError as e:
            pass
        
        try:
            #Verifico che non abbia features associate
            db["context_feature"][{"context":cntxt}]
            raise ValueError(f"Context {cntxt} has features. Can't drop.")
        except KeyError as e:                                             
            pass                                                          
     
        try:
            #Elimino le eventuali connessioni ai genitori
            db["context_context"].pop({"descendant":cntxt})
        except KeyError as e:
            pass

        out.data=db["context"].pop(cntxt).to_dict(orient="records")
    
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
        out.status = falcon.HTTP_CONFLICT

    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return


@hug.delete("/{cntxt}")
def delete_context_endpoint(
    cntxt,
    request=None,
    response=None,
    **kwargs
):


    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
 
    return delete_context_param(cntxt,request,response,**kwargs)


#GET DESCENDANTS LINKS

@hug.get("/{cntxt}/descendants")
def get_descendants_param(
    cntxt,
    descendant=None,
    homogeneous=None,
    dtype=None,
    label=None,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
    out = ResponseFormatter(status=falcon.HTTP_OK)

    cntxt=clean_input(cntxt)

    descendant = clean_input(descendant)

    homogeneous = boolenize(homogeneous,nonevalue=False)

    try:

        out.data=[ c for c in lineages(cntxt,homo_only=homogeneous) if not descendant.__len__() or c in descendant  ]
    
    except ValueError as e:
        out.message = "Context is None: "+str(e)
        out.status = falcon.HTTP_CONFLICT

    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return


@hug.get("/{cntxt}/descendants/{descendant}")
def get_descendants_endpoint(
    cntxt,
    descendant,
    homogeneous=None,
    dtype=None,
    label=None,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
    return get_descendants_param(cntxt=cntxt,homogeneous=homogeneous,descendant=descendant,dtype=dtype,label=label,request=request,response=response,**kwargs)



# POST DESCENDANTS LINKS

@hug.post("/{cntxt}/descendants")
def create_descendants_param(
    cntxt,
    descendant,
    homogeneous=None,
    dtype=None,
    label=None,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

CAVEAT:

    il comportamento del gestore dei parametri in ingresso, a basso livello quello di
    una stringa contenente virgole come un CSV, rimuovendo, però elementi vuoti:
        es.: a,,c diventa [a,c]

    questo comportamento affligge i parametri dtype e label (con trim_none=False nel clean_input)
    che accetterebbero elementi null nella lista
"""

    
    out = ResponseFormatter(status=falcon.HTTP_CREATED)

    cntxt=clean_input(cntxt)
    descendant = clean_input(descendant)

    dtype = clean_input(dtype,trim_none=False)
    label = clean_input(label,trim_none=False)
    homogeneous = clean_input(homogeneous,trim_none=False)
    
    try:
        if not cntxt.__len__():
            raise ValueError ( "cntxt required" )
        if cntxt.__len__() > 1:
            raise ValueError ( "cntxt must be exactly one" )

        if descendant is None:
            raise ValueError ( "descendant required" )

        in_contexts=[*cntxt,*descendant]

        db_contexts=list(db["context"][in_contexts].index)
        
        invalid_contexts=[ a for a in in_contexts if a not in db_contexts ]

        if invalid_contexts.__len__():
            raise ValueError( f"contexts not found:{invalid_contexts}")

        if dtype.__len__() > 1 and dtype.__len__() != descendant.__len__():
            raise ValueError ("dtype length invalid")

        if label.__len__() > 1 and label.__len__() != descendant.__len__():
            raise ValueError ("label length invalid")

        if homogeneous.__len__() > 1 and homogeneous.__len__() != descendant.__len__():
            raise ValueError ("homogeneous length invalid")

        if dtype.__len__() == 1:
            v = dtype[0]
            dtype=[ v for a in descendant ]
    

        if label.__len__() == 1:
            v = label[0]
            label=[ v for a in descendant ]
   

        if homogeneous.__len__() == 1:
            v = homogeneous[0]
            homogeneous=[ v for a in descendant ]

   

        homogeneous=list(map( lambda x: int(boolenize(x,nonevalue=True)), homogeneous ))

        colliders=[]

        for i in range(0,homogeneous.__len__()):
            if homogeneous[i]:
                colliders.append(descendant[i])


        ## RILASSATA LA CONDIZIONE, SE SI TROVANO LINK CON PADRI OMOGENEI 
        ## CON ALTRI CONTESTI (CE NE PUO' ESSERE SOLO UNO) VENGONO RIMOSI 
        homoparented=contexts_with_homo_parent(colliders)

        for relation in homoparented:
            db["context_context"].pop({"ancestor":relation[0],"descendant":relation[1]})

        if homoparented.__len__():
            pass
            #raise ValueError(f"some descendants have already an homogeneous parent: {homoparented}")


        collisions=features_interfamily_collisions(cntxt,colliders,homo_only=True)

        if collisions.__len__():
            raise ValueError(f"some features in descendants are already present in parent family: {collisions}")


        for i in range(0,descendant.__len__()):
            db["context_context"][{"ancestor":cntxt[0],"descendant":descendant[i]}]={"label":label[i],"homogeneous":homogeneous[i],"klass":dtype[i]}

    except Exception as e:
        # raise e #DEBUG
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return

@hug.post("/{cntxt}/descendants/{descendant}")
def create_descendants_endpoint(
    cntxt,
    descendant,
    dtype=None,
    label=None,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""

    return create_descendants_param(cntxt=cntxt,descendant=descendant,dtype=dtype,label=label,request=request,response=response,**kwargs)


@hug.delete("/{cntxt}/descendants")
def delete_descendants_param(
    cntxt,
    descendant,
#   dtype=None,
#   label=None,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
    out = ResponseFormatter(status=falcon.HTTP_OK)

    cntxt=clean_input(cntxt)
    descendant = clean_input(descendant)

    try:
        if not cntxt.__len__():
            raise Exception ( "cntxt required" )
        if cntxt.__len__() > 1:
            raise Exception ( "cntxt must be exactly one" )
        if not descendant.__len__():
            raise Exception ( "descendant required" )

        out.data=db["context_context"].pop({"ancestor":cntxt[0],"descendant":descendant}).to_dict(orient="records")

    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return

@hug.delete("/{cntxt}/descendants/{descendant}")
def delete_descendants_endpoint(
    cntxt,
    descendant,
#    dtype=None,
#    label=None,
    request=None,
    response=None,
    **kwargs
):


    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
 
    return delete_descendants_param(cntxt=cntxt,descendant=descendant,request=request,response=response,**kwargs)


@hug.get("/{cntxt}/family")
def get_family_enpoint(
    cntxt,
    homogeneous=None,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
 
    out = ResponseFormatter(status=falcon.HTTP_OK)

    cntxt=clean_input(cntxt)

    homogeneous = boolenize(homogeneous,nonevalue=False)

    try:
        out.data=family(cntxt,homo_only=homogeneous).to_dict(orient="records")
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return


#GET

@hug.get("/{cntxt}/roots")
def get_roots_param(
    cntxt=None,
    homogeneous=False,
    request=None,
    response=None,
    **kwargs
):

    """
DESCRIZIONE:

PARAMETRI:

OUTPUT:

RESPONSE CODES:

"""
    out = ResponseFormatter(status=falcon.HTTP_OK)

    cntxt=clean_input(cntxt)

    homogeneous=boolenize(homogeneous,nonevalue=False)
    
    try:
        out.data=roots_info(cntxt,homo_only=homogeneous).to_dict(orient="records")
    except KeyError as e:
        out.message = str(e)
        out.status = falcon.HTTP_NOT_FOUND
    except Exception as e:
        out.message = str(e)
        out.status = falcon.HTTP_CONFLICT

    response = out.format(response=response, request=request)

    return





