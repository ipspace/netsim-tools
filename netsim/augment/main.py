#
# Build full-blown topology data structures (nodes, links, global parameter) from high-level topology
#

import netaddr
import os
import sys

# Related modules
from .. import common
from .. import addressing
from .. import augment
from ..providers import Provider
from .. import modules

def transform(topology):
  topology.setdefault('defaults',{})
  augment.topology.check_required_elements(topology)
  augment.topology.adjust_global_parameters(topology)
  topology.Provider = Provider.load(topology.provider,topology.defaults.providers[topology.provider])
  common.exit_on_error()

  topology.nodes = augment.nodes.adjust_node_list(topology.nodes)

  common.exit_on_error()
  if 'links' in topology:
    topology.links = augment.links.adjust_link_list(topology.links)
  common.exit_on_error()

  addressing.setup(topology,topology.defaults)
  modules.adjust_modules(topology)
  modules.node_transform("pre_transform",topology)
  modules.link_transform("pre_transform",topology)

  ndict = augment.nodes.transform(topology,topology.defaults,topology.pools)
  common.exit_on_error()
  if 'links' in topology:
    augment.links.transform(topology.links,topology.defaults,ndict,topology.pools)

  modules.node_transform("post_transform",topology)
  modules.link_transform("post_transform",topology)
  common.exit_on_error()
  del topology.pools
  del topology.Provider
