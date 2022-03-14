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
URL = f'https://cloud.mongodb.com/api/atlas/v1.0/groups/{MONGODB_GROUP_ID}/clusters/{MONGODB_CLUSTER_NAME}/fts/indexes?pretty=true'

def create_atlas_search_index(collection:str, index_name:str):
  data = {
    "collectionName": collection,  # model_field
    "database": DATABASE_NAME,
    "mappings": {
        "dynamic": True
    },
    "name": index_name  # model_field_search
  }
  r = requests.post(URL, auth=HTTPDigestAuth(MONGODB_PUBLIC_KEY, MONGODB_PRIVATE_KEY), verify=False, data=json.dumps(data), headers=HEADERS)
  # r = requests.post(url, auth=HTTPDigestAuth(PUBLIC_KEY, PRIVATE_KEY), verify=False, json=data)

  print(r.status_code)



# PUBLIC_KEY=spxuglvc
# PRIVATE_KEY=5158be5b-9907-4cf5-bf6c-3e72bbc08c39
# GROUP_ID=60f1f429e8541e664146ba6a
# CLUSTER_NAME=falm-development
# curl --user "$PUBLIC_KEY:$PRIVATE_KEY" --digest \
#      --header "Content-Type: application/json" \
#      --include \
#      --request POST "https://cloud.mongodb.com/api/atlas/v1.0/groups/$GROUP_ID/clusters/$CLUSTER_NAME/fts/indexes?pretty=true" \
#      --data '{
#          "collectionName": "model_field",
#          "database": "falm_matt",
#          "mappings": {
#              "dynamic": true
#          },
#          "name": "model_field_search"
#        }'