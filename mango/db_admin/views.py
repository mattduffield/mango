import json, os
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Tuple
import settings
from settings import manager
from mango.db_admin.api import (
  list_database_names,
  create_database,
  drop_database,
  list_collection_names,
  create_collection,
  drop_collection,
  list_collection_indexes,
  create_collection_index,
  drop_collection_index,
  create_atlas_search_index, 
  list_atlas_search_indexes,
  delete_atlas_search_index,
)

router = APIRouter(
  prefix = '/api_admin',
  tags = ['Mongodon Admin']
)

@router.get('/list_database_names')
async def get_database_names(user=Depends(manager)):
  response = list_database_names()
  return response

@router.post('/create_database')
async def create_new_database(database:str, user=Depends(manager)):
  response = create_database(database)
  return response

@router.post('/drop_database')
async def delete_database(database:str, user=Depends(manager)):
  response = drop_database(database)
  return response

@router.get('/list_collection_names')
async def get_collection_names(database:str, user=Depends(manager)):
  response = list_collection_names(database)
  return response

@router.post('/create_collection')
async def create_new_collection(database:str, collection:str, user=Depends(manager)):
  response = create_collection(database, collection)
  return response

@router.post('/drop_collection')
async def delete_collection(database:str, collection:str, user=Depends(manager)):
  response = drop_collection(database, collection)
  return response

@router.get('/list_collection_indexes')
async def get_collection_indexes(database:str, collection:str, user=Depends(manager)):
  response = list_collection_indexes(database, collection)
  return response

@router.post('/create_collection_index')
async def create_new_collection_index(database:str, collection:str, fields:List[Tuple[str, int]], user=Depends(manager)):
  response = create_collection_index(database, collection, fields)
  return response

@router.post('/drop_collection_index')
async def delete_collection_index(database:str, collection:str, index_name:str, user=Depends(manager)):
  response = drop_collection_index(database, collection, index_name)
  return response


@router.post('/create_atlas_search_index')
async def create_search_index(collection:str, index_name:str, user=Depends(manager)):
  response = create_atlas_search_index(collection=collection, index_name=index_name)
  return response

@router.get('/list_atlas_search_indexes')
async def get_search_indexes(collection:str, user=Depends(manager)):
  response = list_atlas_search_indexes(collection=collection)
  return response

@router.delete('/delete_atlas_search_index')
async def delete_search_index(index_id:str, user=Depends(manager)):
  response = delete_atlas_search_index(index_id=index_id)
  return response