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