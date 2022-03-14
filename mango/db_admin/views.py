import json, os
from fastapi import APIRouter, Depends, HTTPException
import settings
from settings import manager
from mango.db_admin.api import create_atlas_search_index, get_atlas_search_indexes

router = APIRouter(
  prefix = '/api_admin',
  tags = ['Mongodon Admin']
)

@router.post('/create_atlas_search_index')
async def create_search_index(collection:str, index_name:str, user=Depends(manager)):
  response = create_atlas_search_index(collection=collection, index_name=index_name)
  return response

@router.get('/get_atlas_search_indexes')
async def get_search_indexes(collection:str, user=Depends(manager)):
  response = get_atlas_search_indexes(collection=collection)
  return response