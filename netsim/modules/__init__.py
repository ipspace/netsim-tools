#
# Dynamic module transformation framework
# 
# Individual configuration modules are defined as Python files within this directory inheriting
# Module class and adding transformation methods
#

import os
import sys
import importlib
import inspect

# Related modules
from .. import common
from ..callback import Callback

class Module(Callback):

  def __init__(self,data):
    pass

  @classmethod
  def load(self,module,data):
    module_name = __name__+"."+module
    obj = self.find_class(module_name)
    if obj:
      return obj(data)
    else:
      return Module(data)

mod_load = {}

def augment_node_data(topology):
  global mod_load

  topology.nodes_map = { n.name : n for n in topology.get('nodes',[]) }

  for n in topology.nodes:
    for m in n.get('module',[]):
      if not mod_load.get(m):
        mod_load[m] = Module.load(m,topology.get(m))
      mod_load[m].call("augment_node_data",n,topology)
