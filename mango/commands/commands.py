# https://github.com/pallets/click
from dotenv import load_dotenv
load_dotenv()
import click
import os
import requests
from csv import DictReader
from mango.db import api
from mango.db import models

__author__ = "Matt Duffield"


import asyncio
from functools import wraps

def coro(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    return asyncio.run(f(*args, **kwargs))

  return wrapper


@click.group()
def main():
  """
  CLI for building web sites
  """
  pass

@main.command()
@click.argument('query')
def search(query):
  """This search and return results corresponding to the given query from Google Books"""
  url_format = 'https://www.googleapis.com/books/v1/volumes'
  query = "+".join(query.split())

  query_params = {
      'q': query
  }

  response = requests.get(url_format, params=query_params)

  click.echo(response.json()['items']) 

@main.command()
@click.argument('id')
def get(id):
  """This return a particular book from the given id on Google Books"""
  url_format = 'https://www.googleapis.com/books/v1/volumes/{}'
  click.echo(id)

  response = requests.get(url_format.format(id))

  click.echo(response.json())

@main.command()
@coro
@click.argument('file_name')
@click.argument('database')
@click.argument('collection')
async def bulk_insert_recyclers(file_name: str, database: str, collection: str):
  """This uploads a CSV file into a given collection"""
  click.echo(f'You are attempting to upload the file: {file_name} into the collection: {collection} of the database: {database}')

  data = {
    "database": database,
    "collection": collection,
    "batch": []
  }
  batch = models.BulkWrite(**data)
  with open(file_name, 'r') as csv_file:
    csv_reader = DictReader(csv_file)
    for row in csv_reader:
      bulk_insert = models.BulkInsert(**{
        "bulk_type": "insert_one",
        "data": {
          'name': row['display_name'], 
          'entity_type': 'recycler', 
          'ship_to_street': row['ship_to_street'], 
          'ship_to_city': row['ship_to_city'], 
          'ship_to_state': row['ship_to_state'], 
          'ship_to_region': row['ship_to_region'], 
          'ship_to_postal_code': row['ship_to_postal_code'], 
          'ship_to_first_name': row['ship_to_first_name'],
          'ship_to_last_name': row['ship_to_last_name'],
          'ship_to_office_number': row['ship_to_office_number'],
          'ship_to_mobile_number': row['ship_to_mobile_number'],
        }
      })
      batch.batch.append(bulk_insert)

  await api.bulk_write(batch)

@main.command()
@coro
@click.argument('file_name')
@click.argument('database')
@click.argument('collection')
async def bulk_insert_products(file_name: str, database: str, collection: str):
  """This uploads a CSV file into a given collection"""
  click.echo(f'You are attempting to upload the file: {file_name} into the collection: {collection} of the database: {database}')

  data = {
    "database": database,
    "collection": collection,
    "batch": []
  }
  batch = models.BulkWrite(**data)
  with open(file_name, 'r') as csv_file:
    csv_reader = DictReader(csv_file)
    for row in csv_reader:
      bulk_insert = models.BulkInsert(**{
        "bulk_type": "insert_one",
        "data": {
          'business_key': row['ProductID'],
          'name': row['ProductName'],
          'penn_alliance_product': row['PennAllianceProduct'],
          'kit_assembled_at_recycler': row['KitAssembledAtRecycler'],
          'qb_picked_up_item': row['QBPickedUpItem'],
          'qb_picked_up_income_account': row['QBPickedUpIncomeAccount'],
          'qb_picked_up_cogs_account': row['QBPickedUpCOGSAccount'],
          'qb_scrap_item': row['QBScrapItem'],
          'qb_scrap_income_account': row['QBScrapIncomeAccount'],
          'qb_scrap_cogs_account': row['QBScrapCOGSAccount'],
          'qb_returned_item': row['QBReturnedItem'],
          'qb_returned_income_account': row['QBReturnedIncomeAccount'],
          'qb_returned_cogs_account': row['QBReturnedCOGSAccount'],
          'classify_upon_receipt': row['ClassifyUponReceipt'],
          'falm_sort_product': row['FALMSortProduct'],
          'is_active': row['Active'],
        }
      })
      batch.batch.append(bulk_insert)

  await api.bulk_write(batch)

@main.command()
@click.argument('app_name')
def start_app(app_name: str):
  """This creates a new app folder"""
  click.echo(f'Creating app: {app_name}')
  init_path = os.path.join(os.path.dirname(__file__), 'templates/init.template')
  forms_path = os.path.join(os.path.dirname(__file__), 'templates/forms.template')
  models_path = os.path.join(os.path.dirname(__file__), 'templates/models.template')
  views_path = os.path.join(os.path.dirname(__file__), 'templates/views.template')
  os.mkdir(app_name)
  os.chdir(app_name)
  with open(init_path, 'r') as init_file:
    init = init_file.read()
    f = open('init.py', 'w')
    f.write(init)
    f.close()
  with open(forms_path, 'r') as form_file:
    forms = form_file.read()
    f = open('forms.py', 'w')
    f.write(forms)
    f.close()
  with open(models_path, 'r') as model_file:
    models = model_file.read()
    m = open('models.py', 'w')
    m.write(models)
    m.close()
  with open(views_path, 'r') as view_file:
    views = view_file.read()
    v = open('views.py', 'w')
    v.write(views)
    v.close()

if __name__ == "__main__":
    main()