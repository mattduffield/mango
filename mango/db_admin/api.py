import requests
from requests.auth import HTTPDigestAuth
import json
import os
from pymongo import MongoClient
from bson import json_util, ObjectId
from typing import List, Tuple

DATABASE_CLUSTER = os.environ.get('DATABASE_CLUSTER')
DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
MONGODB_PUBLIC_KEY = os.environ.get('MONGODB_PUBLIC_KEY')
MONGODB_PRIVATE_KEY = os.environ.get('MONGODB_PRIVATE_KEY')
MONGODB_GROUP_ID = os.environ.get('MONGODB_GROUP_ID')
MONGODB_CLUSTER_NAME = os.environ.get('MONGODB_CLUSTER_NAME')
HEADERS = {'Content-Type': 'application/json'}

uri = f'mongodb+srv://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_CLUSTER}.mongodb.net/{DATABASE_NAME}?retryWrites=true&w=majority'
client = MongoClient(uri)
db = client.test

def list_database_names():
  names = client.list_database_names()
  return names

def create_database(database:str):
  db = client[database]
  collection = 'log'
  log = db[collection]
  new_entry = {'msg': f'Database: {database} created!'}
  result = log.insert_one(new_entry)
  data = json.loads(json_util.dumps({'acknowledged': result.acknowledged, 'inserted_id': result.inserted_id}))
  return data

def drop_database(database:str):
  client.drop_database(database)
  return {'msg': f'Database: {database} dropped!'}

def list_collection_names(database:str):
  entity = client[database]
  names = entity.list_collection_names()
  return names

def create_collection(database:str, collection:str):
  db = client[database]
  entity = db[collection]
  new_entry = {'msg': f'Collection: {collection} created!'}
  result = entity.insert_one(new_entry)
  data = json.loads(json_util.dumps({'acknowledged': result.acknowledged, 'inserted_id': result.inserted_id}))
  return data

def drop_collection(database:str, collection:str):
  db = client[database]
  entity = db[collection]
  entity.drop()
  return {'msg': f'Collection: {collection} dropped from database: {database}!'}

def list_collection_indexes(database:str, collection:str):
  db = client[database]
  entity = db[collection]
  result = entity.index_information()
  return result

def create_collection_index(database:str, collection:str, fields:List[Tuple[str, int]]):
  db = client[database]
  entity = db[collection]
  result = entity.create_index(fields)
  return result

def drop_collection_index(database:str, collection:str, index_name:str):
  db = client[database]
  entity = db[collection]
  entity.drop_index(index_name)
  return {'msg': f'Index: {index_name} dropped from collection: {collection} in database: {database}!'}

def create_atlas_search_index(collection:str, index_name:str):
  url = f'https://cloud.mongodb.com/api/atlas/v1.0/groups/{MONGODB_GROUP_ID}/clusters/{MONGODB_CLUSTER_NAME}/fts/indexes?pretty=true'
  data = {
    "collectionName": collection,  # model_field
    "database": DATABASE_NAME,
    "mappings": {
        "dynamic": True
    },
    "name": index_name  # model_field_search
  }
  r = requests.post(url, auth=HTTPDigestAuth(MONGODB_PUBLIC_KEY, MONGODB_PRIVATE_KEY), verify=False, data=json.dumps(data), headers=HEADERS)
  # r = requests.post(url, auth=HTTPDigestAuth(PUBLIC_KEY, PRIVATE_KEY), verify=False, json=data)
  return r.json()

def list_atlas_search_indexes(collection:str):
  url = f'https://cloud.mongodb.com/api/atlas/v1.0/groups/{MONGODB_GROUP_ID}/clusters/{MONGODB_CLUSTER_NAME}/fts/indexes/{DATABASE_NAME}/{collection}?pretty=true'
  r = requests.get(url, auth=HTTPDigestAuth(MONGODB_PUBLIC_KEY, MONGODB_PRIVATE_KEY), verify=False, headers=HEADERS)
  return r.json()

def delete_atlas_search_index(index_id:str):
  url = f'https://cloud.mongodb.com/api/atlas/v1.0/groups/{MONGODB_GROUP_ID}/clusters/{MONGODB_CLUSTER_NAME}/fts/indexes/{index_id}?pretty=true'
  r = requests.delete(url, auth=HTTPDigestAuth(MONGODB_PUBLIC_KEY, MONGODB_PRIVATE_KEY), verify=False, headers=HEADERS)
  return r.json()

