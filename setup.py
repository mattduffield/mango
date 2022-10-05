from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mango',
    version='0.0.264',
    author='Matthew Duffield',
    author_email='matt.duffield@gmail.com',
    description='Web framework for Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/mattduffield/mango',
    project_urls = {
        "Bug Tracker": "https://github.com/mattduffield/mango/issues"
    },
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'mango_admin=mango.mango_admin.mango_admin:main',
            'manage=mango.commands.commands:main',
        ]
    },
    install_requires=[
      'FastAPI',
      'fastapi-router-controller',
      'fastapi_login',
      'jinja2',
      'jinja2-simple-tags',
      'starlette-wtf',
      'WTForms',
      'WTForms-Components',
      'email_validator',
      'aiofiles',
      'uvicorn',
      'python-dotenv',
      'python-dateutil',
      'python-multipart',
      'python-bsonjs',
      'pymongo',
      'pymongo[srv]',
      'requests',
      'bcrypt',
      'pyjwt',
      'passlib',
      'python-quickbooks',
      'itsdangerous',
      'asana',
      'click',
      'colour',
    ],
)