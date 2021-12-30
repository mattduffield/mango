# https://github.com/pallets/click
import click
import os
import requests
import shutil

__author__ = "Matt Duffield"


def write_file(target_path, file_name):
  with open(target_path, 'r') as target_file:
    content = target_file.read()
    f = open(file_name, 'w')
    f.write(content)
    f.close()

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
@click.argument('project_name')
def start_project(project_name: str):
  """This creates a new project folder"""
  if '-' in project_name or ' ' in project_name:
    raise click.UsageError('Invalid project name. Please use only letter, numbers, and underscores.')
  click.echo(f'Creating project: {project_name}')

  # init_path = os.path.join(os.path.dirname(__file__), 'templates/init.template')
  settings_path = os.path.join(os.path.dirname(__file__), 'templates/settings.template')
  main_path = os.path.join(os.path.dirname(__file__), 'templates/main.template')
  readme_path = os.path.join(os.path.dirname(__file__), 'templates/readme.template')
  env_path = os.path.join(os.path.dirname(__file__), 'templates/env.template')
  templates_src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
  static_path = f'{project_name}/static'
  css_path = f'{project_name}/static/css'
  images_path = f'{project_name}/static/images'
  js_path = f'{project_name}/static/js'
  templates_path = f'{project_name}/templates'

  os.mkdir(project_name)
  os.mkdir(static_path)
  os.mkdir(css_path)
  os.mkdir(images_path)
  os.mkdir(js_path)

  shutil.copytree(templates_src_path, templates_path)

  os.chdir(project_name)
  # os.mkdir(project_name)
  # with open(init_path, 'r') as init_file:
  #   init = init_file.read()
  #   f = open(f'{project_name}/__init__.py', 'w')
  #   f.write(init)
  #   f.close()
  write_file(settings_path, 'settings.py')
  write_file(main_path, 'main.py')
  write_file(readme_path, 'README.md')
  write_file(env_path, '.env')


if __name__ == "__main__":
    main()