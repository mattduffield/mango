import requests
from requests.auth import HTTPDigestAuth
import json
import os

DATABASE_NAME = os.environ.get('DATABASE_NAME')
MONGODB_PUBLIC_KEY = os.environ.get('MONGODB_PUBLIC_KEY')
MONGODB_PRIVATE_KEY = os.environ.get('MONGODB_PRIVATE_KEY')
MONGODB_GROUP_ID = os.environ.get('MONGODB_GROUP_ID')
MONGODB_CLUSTER_NAME = os.environ.get('MONGODB_CLUSTER_NAME')
HEADERS = {'Content-Type': 'application/json'}

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
  print(r.status_code)

def get_atlas_search_indexes(collection:str):
  url = f'https://cloud.mongodb.com/api/atlas/v1.0/groups/{MONGODB_GROUP_ID}/clusters/{MONGODB_CLUSTER_NAME}/fts/indexes/{DATABASE_NAME}/{collection}?pretty=true'
  r = requests.get(url, auth=HTTPDigestAuth(MONGODB_PUBLIC_KEY, MONGODB_PRIVATE_KEY), verify=False, headers=HEADERS)
  print(r.status_code)
