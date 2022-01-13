from typing import (
    Deque, Dict, FrozenSet, List, Literal, Optional, Sequence, Set, Tuple, Type, Union
)
from enum import Enum, IntEnum
from pydantic import BaseModel
from mango.hooks.models import Hook
from mango.hooks import hooks


class User(BaseModel):
  username:str
  actions:List[str] = []

  class Config:
    schema_extra = {
      "example": {
        "username": "Matt",
        "actions": ["admin"]
      }
    }


class Transition(BaseModel):
  trigger:str
  source:str
  dest:str
  permission:Optional[str]
  condition:Optional[str]
  before:List[Hook] = []
  after:List[Hook] = []
  redirect_url:str = ''


class WorkflowRequest(BaseModel):
  database:str
  name:str
  trigger:str
  data:Optional[dict]


class Workflow(BaseModel):
  name:str
  states:List[str]
  transitions:List[Transition]
  current_state:str
  version:int
  is_active:bool


class WorkflowRun(Workflow):
  id:Optional[str]
  data:Optional[dict]


class WorkflowTrigger(BaseModel):
  database:str
  id:str
  trigger:str
  trigger_data:Optional[dict]


class Machine(BaseModel):
  workflow_run:WorkflowRun
  database:str

  def find_next_transition(self, trigger:str = None) -> Transition:
    if trigger:
      transition = next((x for x in self.workflow_run.transitions if x.trigger == trigger and x.source == self.workflow_run.current_state), None)
    else:
      transition = next((x for x in self.workflow_run.transitions if x.source == self.workflow_run.current_state), None)
    return transition

  def can(self, permission:str, user:User):
    # TODO: NEED TO SUPPPORT PERMISSION AT THE USER LEVEL FROM THE SECURITY TOKEN...
    can = next((x for x in user.actions if x == permission), None)
    return can

  async def before(self, transition:Transition):
    # https://gist.github.com/indraniel/da11c4f79c79b5e6bfb8
    for x in transition.before:
      if hasattr(hooks, x.name):
        await getattr(hooks, x.name)(database=self.database, id=self.workflow_run.id, hookData=x.data, data=self.workflow_run.data)
      else:
        raise Exception(f'Hook: {x.name} does not exist!')

  async def after(self, transition:Transition):
    # https://gist.github.com/indraniel/da11c4f79c79b5e6bfb8
    for x in transition.after:
      if hasattr(hooks, x.name):
        await getattr(hooks, x.name)(database=self.database, id=self.workflow_run.id, hookData=x.data, data=self.workflow_run.data)
      else:
        raise Exception(f'Hook: {x.name} does not exist!')

  async def next(self, database:str, trigger:str = None):
    print(f'Attempting to transition to next state (current_state:  {self.workflow_run.current_state})')
    transition = self.find_next_transition(trigger)
    print('transition', transition)
    redirect_url = ''
    if transition:
      # if transition.permission and not user:
      #   raise Exception('This transition requires an authenticated user with permissions!')
      # elif transition.permission and user:
      #   if self.can(permission=transition.permission, user=user):
      #     pass
      #   else:
      #     raise Exception('This user does not have permissions to complete this transition!')

      await self.before(transition)
      self.workflow_run.current_state = transition.dest
      await self.after(transition)
      if transition.redirect_url:
        redirect_url = transition.redirect_url
    return self.workflow_run, redirect_url
