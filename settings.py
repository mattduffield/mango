from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()
import os
from mango.template_utils.utils import configure_templates, register_tags, RenderColTag
from fastapi_login import LoginManager
from mango.auth.models import NotAuthenticatedException
from mango.core.app_loader import init_app_loader, get_apps

templates = configure_templates(directory='templates')
host = None

SESSION_SECRET_KEY = os.environ.get('SESSION_SECRET_KEY')
DATABASE_CLUSTER = os.environ.get('DATABASE_CLUSTER')
DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_URL = os.environ.get('MAILGUN_URL')
MAILGUN_FROM_BLOCK = os.environ.get('MAILGUN_FROM_BLOCK')

manager = LoginManager(
  SESSION_SECRET_KEY, 
  token_url='/auth/login', 
  use_cookie=True,
  cookie_name='mango-cookie',
  default_expiry=timedelta(hours=12),
)
manager.not_authenticated_exception = NotAuthenticatedException

def set_host(app):
  global host
  host = app
  init_app_loader(config_templates=templates, config_host=host)


print(f'DATABASE_CLUSTER: {DATABASE_CLUSTER}')
print(f'DATABASE_USERNAME: {DATABASE_USERNAME}')
print(f'DATABASE_PASSWORD: {DATABASE_PASSWORD}')
print(f'DATABASE_NAME: {DATABASE_NAME}')
print(f'MAILGUN_API_KEY: {MAILGUN_API_KEY}')
print(f'MAILGUN_URL: {MAILGUN_URL}')
print(f'MAILGUN_FROM_BLOCK: {MAILGUN_FROM_BLOCK}')
