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
async def bulk_insert_customers(file_name: str, database: str, collection: str):
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
          'business_key': row['CustomerID'],
          'name': row['DisplayName'],
          'first_name': row['FirstName'],
          'last_name': row['LastName'],
          'street': row['dbo_Users.Street'],
          'unit': row['dbo_Users.Unit'],
          'city': row['dbo_Users.City'],
          'region': row['dbo_Users.Region'],
          'postal_code': row['dbo_Users.PostalCode'],
          'country': row['dbo_Users.Country'],
          'telephone': row['dbo_Users.Telephone'],
          'customer_name': row['CustomerName'],
          'email': row['Email'],
          'qb_class': row['QBClass'],
          'qb_invoice_terms': row['QBInvoiceTerms'],
          'qb_customer_name': row['QBCustomerName'],
          'qb_vendor_name': row['QBVendorName'],
          'rename_consignee_labels': row['RenameCustomerLabels'],
          'tracking_number_prefix': row['TrackingNumPrefix'],
          'tracking_number': row['TrackingNum'],
          'parent_customer_key': row['ParentCustomerID'],
          'tracks_product_quantity': row['TracksProductQuantity'],
          'auto_receive_shipment': row['AutoReceiveShipment'],
          'penn_alliance_vendor': row['PennAllianceVendor (OOL)'],
          'customer_street': row['FALMCustomer.Street'],
          'customer_unit': row['FALMCustomer.Unit'],
          'customer_city': row['FALMCustomer.City'],
          'customer_region': row['FALMCustomer.Region'],
          'customer_postal_code': row['FALMCustomer.PostalCode'],
          'customer_country': row['FALMCustomer.Country'],          
          'customer_telephone': row['FALMCustomer.Telephone'],
          'mobile_phone': row['MobilePhone'],
          'fax': row['Fax'],
          'is_pa_accounting': row['IsPAAccounting'],
          'phone_number': row['Phone#'],
          'is_active': row['Active'],
        }
      })
      batch.batch.append(bulk_insert)

  await api.bulk_write(batch)

@main.command()
@coro
@click.argument('file_name')
@click.argument('database')
@click.argument('collection')
async def bulk_insert_ship_to_customers(file_name: str, database: str, collection: str):
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
          'business_key': row['CustomerID'],
          'name': row['DisplayName'],
          'ship_to_first_name': row['FirstName'],
          'ship_to_last_name': row['LastName'],
          'ship_to_street': row['Street'],
          'ship_to_city': row['City'],
          'ship_to_region': row['Region'],
          'ship_to_postal_code': row['PostalCode'],
          'ship_to_email': row['Email'],
          'ship_to_phone_number': row['Phone #'],
          'ship_to_telephone': row['Telephone'],
          'penn_alliance_vendor': bool(row['OnOffLogistics']),
          'is_active': True,
        }
      })
      batch.batch.append(bulk_insert)

  await api.bulk_write(batch)

@main.command()
@coro
@click.argument('file_name')
@click.argument('database')
@click.argument('collection')
async def bulk_insert_bill_to_customers(file_name: str, database: str, collection: str):
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

      bulk_update = models.BulkUpdate(**{
        'bulk_type': 'update_one',
        'query': {
          'business_key': row['CustomerID']
        },
        'data': {
          '$set': {
            'bill_to_first_name': row['FirstName'],
            'bill_to_last_name': row['LastName'],
            'bill_to_street': row['dbo_Users.Street'],
            'bill_to_unit': row['dbo_Users.Unit'],
            'bill_to_city': row['dbo_Users.City'],
            'bill_to_region': row['dbo_Users.Region'],
            'bill_to_postal_code': row['dbo_Users.PostalCode'],
            'bill_to_country': row['dbo_Users.Country'],
            'bill_to_telephone': row['dbo_Users.Telephone'],
            'bill_to_email': row['Email'],
            'bill_to_phone_number': row['Phone#'],
            'bill_to_mobile_phone': row['MobilePhone'],
            'bill_to_fax': row['Fax'],
            'customer_name': row['CustomerName'],
            'qb_class': row['QBClass'],
            'qb_invoice_terms': row['QBInvoiceTerms'],
            'qb_customer_name': row['QBCustomerName'],
            'qb_vendor_name': row['QBVendorName'],
            'rename_consignee_labels': row['RenameCustomerLabels'],
            'tracking_number_prefix': row['TrackingNumPrefix'],
            'tracking_number': row['TrackingNum'],
            'parent_customer_key': row['ParentCustomerID'],
            'tracks_product_quantity': True if row['TracksProductQuantity'] == 'TRUE' else False,
            'auto_receive_shipment': True if row['AutoReceiveShipment'] == 'TRUE' else False,
            'is_pa_accounting': True if row['IsPAAccounting'] == 'TRUE' else False,
          }
        }
      })
      batch.batch.append(bulk_update)

  await api.bulk_write(batch)

@main.command()
@coro
@click.argument('file_name')
@click.argument('database')
@click.argument('collection')
async def bulk_insert_ship_to_recyclers(file_name: str, database: str, collection: str):
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
          'business_key': row['RecyclerID'],
          'name': row['DisplayName'], 
          'ship_to_first_name': row['FirstName'],
          'ship_to_last_name': row['LastName'],
          'ship_to_street': row['Street'], 
          'ship_to_city': row['City'], 
          'ship_to_state': row['Region'], 
          'ship_to_postal_code': row['PostalCode'], 
          'ship_to_country': 'United States',
          'ship_to_email': row['Email'],
          'ship_to_telephone': row['Telephone'],
        }
      })
      batch.batch.append(bulk_insert)

  await api.bulk_write(batch)

@main.command()
@coro
@click.argument('file_name')
@click.argument('database')
@click.argument('collection')
async def bulk_insert_bill_to_recyclers(file_name: str, database: str, collection: str):
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

      bulk_update = models.BulkUpdate(**{
        'bulk_type': 'update_one',
        'query': {
          'business_key': row['RecyclerID']
        },
        'data': {
          '$set': {
            'bill_to_first_name': row['FirstName'],
            'bill_to_last_name': row['LastName'],
            'bill_to_street': row['Street'],
            'bill_to_unit': '',
            'bill_to_city': row['City'],
            'bill_to_state': row['Region'],
            'bill_to_postal_code': row['PostalCode'],
            'bill_to_country': row['Country'],
            'bill_to_telephone': row['Telephone'],
            'bill_to_email': row['Email'],
            'is_pa_accounting': True if row['PennAllianceRecycler'] == 'TRUE' else False,
          }
        }
      })
      batch.batch.append(bulk_update)

  await api.bulk_write(batch)

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