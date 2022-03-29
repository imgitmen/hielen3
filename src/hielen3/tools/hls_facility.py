# coding: utf-8
import boto3
from boto3 import Session
from pycognito import Cognito
import requests
from time import sleep
from random import random
from hielen3 import db,conf
from hielen3.utils import uuid
from datetime import datetime, timedelta
import json
from threading import Thread

resources=["21C04004","22D01001","22D01002","22D01003","22D01005","22D01006","22D01009","22D01011","22D01012","22D01015","22D01016","22D01017","22D01018","22D01019"]

def __parse_out__(out):
    try:
        return json.loads(out.to_json(orient='records'))[0]
    except Exception as e:
        return {}


def manage_stream(resource,creds,timeout=10,times=20,destroytime=120):

    #creds_=conf["aws"]["options"]
    #creds.update(creds_)

    session=Session(**creds)

    try:
        endpoint = session.client('kinesisvideo').get_data_endpoint(StreamName=f'stream-{resource}',APIName='GET_HLS_STREAMING_SESSION_URL')['DataEndpoint']
        client_kvac = session.client('kinesis-video-archived-media',endpoint_url=endpoint)
    except Exception as e:
        db['resources_queues'][resource,uuid()]={
                "status":"GONE", 
                "timestamp": str(datetime.now()),
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
            out=__parse_out__(db['resources_queues'][resource])
            out["status"]="AVAILABLE"
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

            """
            try:
                while True:
                    sleep(destroytime)
                    print(client_kvac.get_hls_streaming_session_url(**req)['HLSStreamingSessionURL'])
            except Exception as e:
                out["status"]="GONE"
                print (out["status"])
                db['resources_queues'][resource]=out
                return
            """

        except KeyError as e:
            return

        except Exception as e:
            out["status"]="PENDING"
            print (out["status"])
            db['resources_queues'][resource]=out

        print (out["status"])
        sleep(timeout)

    try:
        out=__parse_out__(db['resources_queues'][resource])
        out["status"]="TIMEOUT"
        print (out["status"])
        db['resources_queues'][resource]=out
    except KeyError:
        pass



def start_stream(resource=None):

    out={}
    outcode=200

    if resource is None:
        resource=resources[int(random()*100)%resources.__len__()]

    try:
        out=__parse_out__(db['resources_queues'][resource])
    except KeyError as e:
        out=None

    if out is None or out['status'] in ["TIMEOUT","GONE"]:
        try:
            db['resources_queues'].pop([out['resource'],out['queue']])
        except KeyError:
            pass
        except TypeError:
            pass

        u=Cognito(**conf["aws"]["pool"])
        u.authenticate(conf["aws"]["pwd"])

        headers={"Authorization":u.id_token}

        url_creds ="https://api.wsn-cloud.com/api/portal/get_stream_viewer_creds"
        res=requests.get(url=url_creds,headers=headers)

        creds=res.json()

        creds={
                'aws_access_key_id':creds['access_id'],
                'aws_secret_access_key':creds['secret_key'],
                "region_name": "eu-west-1"
                }

        url_cmmnd ="https://api.wsn-cloud.com/api/portal/post_command"

        data={"wsn_sn": resource, "command_code": 8, "command_args":["1"]}

        res=requests.post(url=url_cmmnd,json=data,headers=headers)

        #print (res.__dict__)

        if res.status_code in [ 200, 409 ]:
            db['resources_queues'][resource,uuid()]={
                    "status":"INIT", 
                    "timestamp": str(datetime.now()), 
                    "url":None }
     
            out=__parse_out__(db['resources_queues'][resource])

            Thread(target=manage_stream,args=(resource,creds),daemon=True).start()

        outcode=res.status_code

    return out,outcode 


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

    return __parse_out__(out),outcode






