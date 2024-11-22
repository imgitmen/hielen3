#!/usr/bin/env python
# coding=utf-8
import hug
from pycognito import Cognito
import requests
import falcon
from hielen3.utils import ResponseFormatter
from hielen3 import db, conf

def changerate(serial,time):

    if time is None:
        time = 0

    time = int(time)

    if time < 1:
        raise Exception ("new rate under minute")


    time=time*60
    c=Cognito(**conf["aws"]["pool"])
    c.authenticate(conf["aws"]["pwd"])
    headers={"Authorization":c.id_token}
    url_cmnd='https://0xnsi8bx82.execute-api.eu-west-1.amazonaws.com/Dev/portal/post_command'
    data= {"wsn_sn":serial,"command_code": 2,"command_args":['"'+str(time)+'"']}

    res=requests.post(url=url_cmnd,json=data,headers=headers)
    return res

@hug.get("/")
def gettime(features=None,request=None,response=None):

    out = ResponseFormatter()

    q='select * from v_feature_rfiponti_timerate'


    if features is not None:
        if not isinstance(features,list):
            features=[features]
        features=",".join('"'+str(a)+'"' for a in features)
        q=f"{q} where feature in ({features})" 


    try:
        out.data=db['query'][q][['feature','minutes']].to_dict(orient='records')
    except Exception as e:
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"feature not found: {features}"

    out.format(request=request,response=response) 

    return
    


@hug.get("/{feature}")
def gettimer(feature=None,request=None,response=None):
    return gettime(features=feature,request=request,response=response)



@hug.post("/{feature}")
def chtime(feature,newrate,request=None, response=None):

    out = ResponseFormatter()

    serial=db['query'][f'select * from v_feature_rfiponti_timerate where feature={feature!r}']['serial'].squeeze().replace("'","")


    print ("\n",serial,"\n")

    try:
        res=changerate(serial,newrate)
        print (res.__dict__)
    except Exception as e:
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"something gone wrong: {e}"
        out.format(request=request,response=response) 
        return 

    stat = f"REPLACE into feature_rfiponti_timerate VALUES ({feature!r},{newrate})"

    try:
        en=db['query'].engine
        with en.begin() as conn:
            conn.execute('start transaction')
            conn.execute(stat)
        en.dispose()
    except Exception as e:
        out.status = falcon.HTTP_NOT_FOUND
        out.message = f"something gone wrong {e}"
        out.format(request=request,response=response) 
        return out

    return gettimer(feature=feature,request=request,response=response)


