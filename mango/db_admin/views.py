import json, os
from fastapi import APIRouter, Depends, HTTPException
import settings
from settings import manager
from mango.db_admin.api import (
  list_database_names,
  create_database,
  drop_database,
  list_collection_names,
  create_collection,
  drop_collection,
  create_atlas_search_index, 
  get_atlas_search_indexes,
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

@router.post('/create_atlas_search_index')
async def create_search_index(collection:str, index_name:str, user=Depends(manager)):
  response = create_atlas_search_index(collection=collection, index_name=index_name)
  return response

@router.get('/get_atlas_search_indexes')
async def get_search_indexes(collection:str, user=Depends(manager)):
  response = get_atlas_search_indexes(collection=collection)
  return response