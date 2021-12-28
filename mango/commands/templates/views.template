from fastapi import Request
from fastapi.responses import HTMLResponse
from typing import (
    Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)
from fastapi_router_controller import Controller
from mango.core.views import (
  CreateView,
  UpdateView,
  DeleteView, 
  ListView, 
  get_controller,
  GenericListView,
)
from mango.db.query import datetime_parser, json_from_mongo, Credentials, Query, QueryOne, Count, InsertOne, InsertMany, Update, Delete, BulkWrite, AggregatePipeline
from mango.db.api import find, find_one
from settings import templates, DATABASE_NAME
