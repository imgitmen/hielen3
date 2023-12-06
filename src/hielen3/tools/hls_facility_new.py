# coding: utf-8
import boto3
from boto3 import Session
from pycognito import Cognito
import requests
from time import sleep
from random import random
#from hielen3 import db,conf
#from hielen3.utils import uuid, dataframe2jsonizabledict
from numpy import datetime64, timedelta64 
import json
from threading import Thread



conf={
    "apppath":"/home/fantamodeman/SVILUPPOandTESTING/python_sandbox/dev/modules/hielen3/src",
    "host":"localhost",
    "db_maria_connection":{
                "dialect":"mariadb",
                "usr":"editor",
                "pwd":"rincostocastico",
                "host":"127.0.0.1",
                "port":13231,
                "db":"geoframe"
            },
    "aws":{
        "options":{ 
            "aws_access_key_id": "AKIAQRBSYFZF3U5FZDEL",
            "aws_secret_access_key": "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",
            "region_name": "eu-west-1"
        },
        "pool":{
            "user_pool_id":"eu-west-1_A6bkbncVk",
            "client_id":"5cfm2ro7dscjkkglac3mti24vl",
            "username":"digregorio@img-srl.com"
        },
        "pwd":"Kaos.6969"
    },
    "server_time_offset":1
}

def manage_stream(resource,timeout=10,times=20,destroytime=120):

    u=Cognito(**conf["aws"]["pool"])
    u.authenticate(conf["aws"]["pwd"])

    headers={"Authorization":u.id_token}

    url_creds ="https://api.wsn-cloud.com/api/portal/get_stream_viewer_creds"
    res=requests.get(url=url_creds,headers=headers)

    try:
        if res.status_code in [ 200, 409 ]:
            creds=res.json()

            creds={
                    'aws_access_key_id':creds['access_id'],
                    'aws_secret_access_key':creds['secret_key'],
                    "region_name": "eu-west-1"
                    }

            url_cmmnd ="https://api.wsn-cloud.com/api/portal/post_command"

            data={"wsn_sn": resource, "command_code": 8, "command_args":["1"]}

            res=requests.post(url=url_cmmnd,json=data,headers=headers)

            session=Session(**creds)
        else:
            raise Exception('wrong code')

        endpoint = session.client('kinesisvideo').get_data_endpoint(StreamName=f'stream-{resource}',APIName='GET_HLS_STREAMING_SESSION_URL')['DataEndpoint']
        client_kvac = session.client('kinesis-video-archived-media',endpoint_url=endpoint)

    except Exception as e:
        db['resources_queues'][resource,uuid()]={
                "status":"GONE", 
                "timestamp": str(datetime64("now")),
                "url":None }
        return


    req = {
            "StreamName": f"stream-{resource}",
            "PlaybackMode": "LIVE",
            "HLSFragmentSelector": {
                "FragmentSelectorType": "PRODUCER_TIMESTAMP"
            },
            "ContainerFormat": "FRAGMENTED_MP4",
            "DiscontinuityMode": "ALWAYS",
            "DisplayFragmentTimestamp": "ALWAYS",
    }

    for i in range(times):
        print (f"resource: {resource}, time: {timeout*i} secs")
        try:
            out=dataframe2jsonizabledict(db['resources_queues'][resource])
            out["status"]="AVAILABLE"
            out["timestamp"]=str(datetime64("now"))
        except KeyError:
            return
        
        try:
            out["url"]=client_kvac.get_hls_streaming_session_url(**req)['HLSStreamingSessionURL']
            db['resources_queues'][resource]=out

            try:
                sleep(destroytime)
            except Exception:
                pass
            finally:
                out["status"]="GONE"
                print (out["status"])
                db['resources_queues'][resource]=out
                return

        except KeyError as e:
            return

        except Exception as e:
            out["status"]="PENDING"
            print (out["status"])
            db['resources_queues'][resource]=out

        print (out["status"])
        sleep(timeout)

    try:
        out=dataframe2jsonizabledict(db['resources_queues'][resource])
        out["status"]="TIMEOUT"
        print (out["status"])
        db['resources_queues'][resource]=out
    except KeyError:
        pass

def start_stream(resource=None):

    out={}

    if resource is None:
        raise KeyError('No resource')

    try:
        out=dataframe2jsonizabledict(db['resources_queues'][resource])
    except KeyError as e:
        out=None

    nowtime=datetime64("now")


    #if out is None or out['status'] in ["TIMEOUT","GONE","INIT"]:

    try:
        if out['status'] in ["TIMEOUT","GONE"]:
            raise Exception

        if ( nowtime-datetime64(out["timestamp"]) ) < timedelta64(1200):
            return out
    except Exception as e:
        pass

    try:
        db['resources_queues'].pop([out['resource'],out['queue']])
    except KeyError:
        pass
    except TypeError:
        pass
    
    try:
        db['resources_queues'][resource,uuid()]={
                    "status":"INIT", 
                    "timestamp": str(nowtime), 
                    "url":None }

        out=dataframe2jsonizabledict(db['resources_queues'][resource])

        Thread(target=manage_stream,args=(resource,),daemon=True).start()
    except Exception as e:
        pass

    return out 


def get_stream(queue):

    out={}
    outcode=200

    if queue is None:
        outcode=400
    else:
        try:
            out=db['resources_queues'][:,queue]
        except KeyError as e:
            outcode=404

    return out,outcode






