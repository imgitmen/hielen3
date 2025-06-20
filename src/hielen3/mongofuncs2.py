import uuid, glob, os, sys
import certifi
import pandas as pd
from datetime import datetime
from uuid import UUID
from bson.objectid import ObjectId
from pymongo import MongoClient, UpdateOne
from pprint import pprint

def connecting(uri, db, col, user, pw, cert):

#    use this if tls/ssl connections activated
#    client = MongoClient(uri, uuidRepresentation='standard', username = user, password = pw, tls=True, tlsCAFile=certifi.where(), tlsCertificateKeyFile=cert, tlsAllowInvalidCertificates=True)
     if (user is None) & (pw is None):
        client = MongoClient(uri, uuidRepresentation='standard')
     else:
        client = MongoClient(uri, uuidRepresentation='standard', username = user, password = pw)
     database = client[db]
     collection = database[col]
     return client, collection
#def insertUpdate(uri, db, col, df, uui, user, pw, **kwargs):
def insertUpdate(uri, db, col, df, uui, **kwargs):
    cert = kwargs.get("cert")
    user = kwargs.get("user")
    pw = kwargs.get("pw")
    client, coll = connecting(uri, db, col, user, pw, cert)
    df1 = pd.DataFrame(df)
    dd = df1['DATE'].sort_values().head(1).reset_index()
    date = int(dd['DATE'].iloc[0])
    dd = list(df1['DATE']+df1['TIME'])
    df1['DATE'] = date
    df1['ts'] = dd - df1['DATE']
    df1 = df1.drop('TIME', axis=1)
    mintime = min(dd)
    maxtime = max(dd)
    pipe = [{"$match": {"uuid": uui}},\
            {"$addFields": \
            {"ttt" :{"$arrayElemAt": [ "$ts_val", 0]},"ts": {"$arrayElemAt": [ "$ts_val", 0]}, "val": {"$arrayElemAt": [ "$ts_val", -1]}}},\
            {"$unwind": "$ts"},\
            {"$addFields": \
            {"time": {"$add":["$ts", "$Date"]}, "index": {"$indexOfArray": ["$ttt", "$ts"]}}},\
            {"$addFields":{"value": {"$arrayElemAt": ["$val", "$index"]}}},\
            {"$match": { "time": {'$gte': mintime, '$lte': maxtime}}},\
            {"$project": {"uuid": 0, "Date": 0, "ts_val": 0, "ts" : 0, "val": 0, "ttt" : 0}}]
    res = pd.DataFrame(list(coll.aggregate(pipe)), columns = ['_id','time', 'index', 'value'])
#   timelist = list(res['time'])
    ins = []
    updates = []
    dd_series = pd.Series(dd)
    timelist_series = pd.Series(list(res['time']))
    # Create a DataFrame for dd with indices and values
    dd_df = pd.DataFrame({'index_dd': dd_series.index, 'val_dd': dd_series.values})

    # Create a DataFrame for timelist with indices and values
    timelist_df = pd.DataFrame({'index_timelist': timelist_series.index, 'val_timelist': timelist_series.values})
    # Merge both DataFrames on the values
    merged_df = pd.merge(dd_df, timelist_df, left_on='val_dd', right_on='val_timelist', how='inner')

    # Merge the resulting DataFrame with the res DataFrame to get the necessary columns
    final_df = pd.merge(merged_df, res, left_on='index_timelist', right_index=True)
    # Prepare updates using vectorized operations
    updates = final_df.apply(lambda row: UpdateOne({'_id': row['_id']},{'$set': {'ts_val.1.' + str(row['index']): df1.at[row['index_dd'], 'val']}}), axis=1).values.tolist()
    countupd = len(updates)
    # Find indices in dd not present in timelist
    ins = dd_series[~dd_series.isin(timelist_series)].index.tolist()
    #creating chunks of 1kb per each write

    if countupd==0:
        df_ins = df1
    elif len(ins)>0:
        df_ins = pd.DataFrame(df1.iloc[i,:] for i in ins).reset_index()
    else:
        df_ins = pd.DataFrame(columns=['DATE', 'val', 'ts'])
    ls = [uui, date]
    data = pd.DataFrame(columns=['uuid', 'Date', 'ts_val'])
    ts = []
    val = []
    m = 0
    for i in range(0, len(df_ins)):
            k = 800
            r = float(df_ins['ts'].iloc[i])
            v = df_ins['val'].iloc[i]
            k -= (m/2)
            if (k <= 0 and i != len(df_ins)-1):
               ls.append([ts, val])
               data = pd.concat([data, pd.DataFrame([ls], columns = ['uuid', 'Date', 'ts_val'])], ignore_index=True)
               ts = [r]
               val = [v]
               ls = [uui, date]
               m = (sys.getsizeof(v)+sys.getsizeof(r))
            elif(i == len(df_ins)-1):
               ts.append(r)
               val.append(v)
               ls.append([ts, val])
               data = pd.concat([data, pd.DataFrame([ls], columns = ['uuid', 'Date', 'ts_val'])], ignore_index=True)
            else:
               ts.append(r)
               m += (sys.getsizeof(v)+sys.getsizeof(r))
               val.append(v)
    with client.start_session() as session:
        session.start_transaction()
        try:
           if len(updates)>0:
              coll.bulk_write(updates)
           else:
              pass
           if not data.empty:
              convert_dict = data.to_dict(orient="records")
              coll.insert_many(convert_dict)
              print('Total data count: '+str(len(df1))+'\n'+'Number of MongoDB Inserts: '+str(len(data))+\
                '\n'+'number of updates done: '+ str(countupd)+'\n'+'number of inserts done: '+str(len(ins))+\
                '\n'+'Each document has "ts, val" fields of len: '+str(len(data['ts_val'][0][0]))+' and a few documents may have +/- 1'+\
                '\n'+'Except The last document of insert has: '+str(len(list(data['ts_val'])[-1][0])))
           else:
              print('Total data count: '+str(len(df1))+'\n'+'Number of MongoDB Inserts: '+str(len(data))+\
                '\n'+'number of updates done: '+ str(countupd)+'\n'+'No insert action took place')
        except Exception as e:
           print("An error occurred:", e)
           session.abort_transaction()
    client.close()
    return
#def fetch(uri, db, col, uui, user, pw, **kwargs):
def fetch(uri, db, col, uui, **kwargs):
    cert = kwargs.get("cert")
    user = kwargs.get("user")
    pw = kwargs.get("pw")
    client, coll = connecting(uri, db, col, user, pw, cert)
    TIme1 = kwargs.get("time1")
    TIme2 = kwargs.get("time2")

    pipe = [
      {
        "$match": {
          "uuid": { "$in": uui }
        }
      },
      {
        "$addFields": {
          "ts": { "$arrayElemAt": [ "$ts_val", 0 ] },
          "val": { "$arrayElemAt": [ "$ts_val", 1 ] }
        }
      },
      {
        "$unwind": {
          "path": "$ts",
          "includeArrayIndex": "i"
        }
      },
      {
        "$addFields": {
          "value": { "$arrayElemAt": [ "$val", "$i" ] },
          "timestamp": { "$add": [ "$ts", "$Date" ] }
        }
      },
      {
        "$match": {
          "$expr": {
            "$and": [
              {
                "$or": [
                  { "$eq": [ TIme1, None ] },
                  { "$gte": [ "$timestamp", TIme1 ] }
                ]
              },
              {
                "$or": [
                  { "$eq": [ TIme2, None ] },
                  { "$lte": [ "$timestamp", TIme2 ] }
                ]
              }
            ]
          }
        }
      },
      {
        "$project": {
          "_id": 0,
          "uuid": 1,
          "timestamp": 1,
          "value": 1
        }
      }
    ]

    #res = pd.DataFrame(list(coll.aggregate(pipe)))

    res = pd.DataFrame(list(coll.aggregate(pipe)))

    try:
        res["uuid"]=res["uuid"].apply(str)
    except Exception as e:
        raise KeyError(res)
    

    #res.rename(columns = {'value': uui, 'time':'Timestamp'},inplace = True)
    client.close()
    return res

def deletes(uri, db, col, uui, time1, **kwargs):
    cert = kwargs.get("cert")
    user = kwargs.get("user")
    pw = kwargs.get("pw")
    client, coll = connecting(uri, db, col, user, pw, cert)
    TIme2 = kwargs.get("time2")
    if TIme2 is not None:
        pipe = [{"$match": {"uuid": uui}},\
            {"$addFields": \
            {"ttt" :{"$arrayElemAt": [ "$ts_val", 0]},"ts": {"$arrayElemAt": [ "$ts_val", 0]}, "val": {"$arrayElemAt": [ "$ts_val", -1]}}},\
            {"$unwind": "$ts"},\
            {"$addFields": \
            {"time": {"$add":["$ts", "$Date"]}, "index": {"$indexOfArray": ["$ttt", "$ts"]}}},\
            {"$addFields":{"value": {"$arrayElemAt": ["$val", "$index"]}}},\
            {"$match": { "time": {'$gte': time1, '$lte': TIme2}}},\
            {"$project": {"uuid": 0, "Date": 0, "ts_val": 0, "ts" : 0, "val": 0, "ttt" : 0}}]
    else:
        pipe = [{"$match": {"uuid": uui}},\
            {"$addFields": \
            {"ttt" :{"$arrayElemAt": [ "$ts_val", 0]},"ts": {"$arrayElemAt": [ "$ts_val", 0]}, "val": {"$arrayElemAt": [ "$ts_val", -1]}}},\
            {"$unwind": "$ts"},\
            {"$addFields": \
            {"time": {"$add":["$ts", "$Date"]}, "index": {"$indexOfArray": ["$ttt", "$ts"]}}},\
            {"$addFields":{"value": {"$arrayElemAt": ["$val", "$index"]}}},\
            {"$match": { "time": {'$gte': time1}}},\
            {"$project": {"uuid": 0, "Date": 0, "ts_val": 0, "ts" : 0, "val": 0, "ttt" : 0}}]
    res = pd.DataFrame(list(coll.aggregate(pipe)))
    with client.start_session() as session:
       session.start_transaction()
       try:
          dlt = res.apply(lambda row: UpdateOne({'_id': row['_id']}, {"$unset": {\
            'ts_val.1.' + str(row['index']): 1,\
            'ts_val.0.' + str(row['index']): 1}}),axis=1).values.tolist()
          coll.bulk_write(dlt)
          coll.update_many({}, {"$pull" : {'ts_val.1': None, 'ts_val.0':None}})
          coll.delete_many({ 'ts_val': { '$exists': True, '$eq': [] } })
          print(res)
          print('Deleting number of Time and Values: '+ str(len(dlt)))
       except Exception as e:
          print("An error occurred:", e)
          session.abort_transaction()
    client.close()
    return
