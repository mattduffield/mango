# https://github.com/pallets/click
import click
import os
import requests

__author__ = "Matt Duffield"


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
@click.argument('project_name')
async def start_project(project_name: str):
  """This creates a new project folder"""
  click.echo(f'Creating project: {project_name}')
  settings_path = os.path.join(os.path.dirname(__file__), 'templates/settings.template')
  main_path = os.path.join(os.path.dirname(__file__), 'templates/main.template')
  os.mkdir(project_name)
  os.chdir(project_name)
  with open(settings_path, 'r') as settings_file:
    settings = settings_file.read()
    f = open('settings.py', 'w')
    f.write(settings)
    f.close()
  with open(main_path, 'r') as main_file:
    main = main_file.read()
    f = open('main.py', 'w')
    f.write(main)
    f.close()

if __name__ == "__main__":
    main()