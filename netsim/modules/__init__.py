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
from box import Box

# Related modules
from .. import common
from ..callback import Callback
from ..augment.nodes import rebuild_nodes_map

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

# Set default list of modules for nodes without specific module list
#
def augment_node_module(topology):
  if not 'module' in topology:
    return

  module = topology['module']
  for n in topology.nodes:
    if not 'module' in n:
      n.module = module

# Merge global module parameters with per-node module parameters
#
def merge_node_module_params(topology):
  for n in topology.nodes:
    if 'module' in n:
      for m in n.module:
        if m in topology:
          n[m] = topology[m] + n[m]

'''
adjust_modules: last phase of global module adjustments

* add node-specific modules into global list of modules after the node
  modules have been set to default global values
* merge default settings with global settings
'''
def adjust_global_modules(topology):
  mod_dict = { m : None for m in topology.get('module',[]) }
  for n in topology.nodes:
    for m in n.get('module',[]):
      mod_dict[m] = None

  if not mod_dict:
    return

  topology.module = list(mod_dict.keys())
  for m in topology.module:
    if topology.defaults.get(m):
      default_copy = Box(topology.defaults[m])

      if 'no_propagate' in default_copy:
        for remove_key in default_copy.no_propagate:
          default_copy.pop(remove_key,None)
        default_copy.pop('no_propagate')

      topology[m] = default_copy + topology[m]

'''
adjust_modules: somewhat intricate multi-step config module adjustments

* Set node default modules based on global modules
* Adjust global module list based on node modules + copy default settings into topology settings
* Merge global module parametres into nodes
'''
def adjust_modules(topology):
  augment_node_module(topology)
  adjust_global_modules(topology)
  merge_node_module_params(topology)

"""
Callback transformation routines

* node_transform: for all nodes, call specified method for every module used by the node
* link_transform: for all links, call specified method for every module used by any node on the link

Note: mod_load is a global cache of loaded modules
"""

mod_load = {}

def node_transform(method,topology):
  global mod_load

  rebuild_nodes_map(topology)

  for n in topology.nodes:
    for m in n.get('module',[]):
      if not mod_load.get(m):
        mod_load[m] = Module.load(m,topology.get(m))
      mod_load[m].call("node_"+method,n,topology)

def link_transform(method,topology):
  global mod_load

  rebuild_nodes_map(topology)
  for l in topology.get("links",[]):
    mod_list = {}
    for n in l.keys():
      if not n in topology.nodes_map:
        continue
      mod_list.update({ m: None for m in topology.nodes_map[n].get("module",[]) })
    for m in mod_list.keys():
      if not mod_load.get(m):
        mod_load[m] = Module.load(m,topology.get(m))
      mod_load[m].call("link_"+method,l,topology)