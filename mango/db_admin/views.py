import json, os
from fastapi import APIRouter, Depends, HTTPException
import settings
from settings import manager
from api import create_atlas_search_index

router = APIRouter(
  prefix = '/api_admin',
  tags = ['Mongodon Admin']
)

@router.post('/create_atlas_search_index')
async def find(collection:str, index_name:str, user=Depends(manager)):
  response = create_atlas_search_index(collection=collection, index_name=index_name)
  return response