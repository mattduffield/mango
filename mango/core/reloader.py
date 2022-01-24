'''
reloader.py: Reloads nested modules recursively.

https://docs.gunicorn.org/en/stable/signals.html
https://levelup.gitconnected.com/how-to-restart-fastapi-server-with-bash-script-f05a5bfcec5c
https://discuss.erpnext.com/t/gracefully-reload-gunicorn-for-changes-to-python-code/55207
https://gist.github.com/TheWaWaR/10955091
https://github.com/alphagov/unicornherder
https://www.programcreek.com/python/example/90252/importlib.reload

https://dev.to/fronkan/importlib-reload-for-resting-modules-between-tests-neh
https://github.com/tiangolo/fastapi/issues/4257
https://gist.github.com/bart314/f1a9fcaaf25e1e8e47695c3e073f5727
https://bayesianbrad.github.io/posts/2017_loader-finder-python.html
https://www.oreilly.com/library/view/python-cookbook/0596001673/ch14s02.html
'''

import types
from importlib import reload

def status(module):
  print(f'Reloading {module.__name__}')

def try_reload(module):
  try:
    reload(module)
  except:
      print('FAILED: %s' % module)

def recursive_reload(objects, visited):
  for obj in objects:
    if type(obj) == types.ModuleType and obj not in visited:
        status(obj)
        try_reload(obj)
        visited.add(obj)
        recursive_reload(obj.__dict__.values(), visited)

def reload_all(*args):
  recursive_reload(args, set())

# def recursive_reload(module, visited):
#   if not module in visited:
#     status(module)
#     try_reload(module)
#     visited[module] = True
#     for attrobj in module.__dict__.values():
#       if type(attrobj) == types.ModuleType:
#         recursive_reload(attrobj, visited)

# def reload_all(*args):
#   visited = {}
#   for arg in args:
#     if type(arg) == types.ModuleType:
#       recursive_reload(arg, visited)


