#
# BGP transformation module
#

from box import Box
import netaddr

from . import Module
from .. import common

def check_bgp_parameters(node):
  if "bgp" in node:
    if not "as" in node.bgp:
      common.error("Node %s has BGP enabled but no AS number specified" % node.name)

def find_bgp_rr(bgp_as,topology):
  rrlist = []
  for n in topology.nodes:
    if not "bgp" in n:
      continue
    if n.bgp["as"] == bgp_as and n.bgp.get("rr",None):
      rrlist.append(n)
  return rrlist

def bgp_neighbor(n,intf):
  ngb = Box({},default_box=True,box_dots=True)
  ngb.name = n.name
  ngb["as"] = n.bgp.get("as")
  for af in ['ipv4','ipv6']:
    if af in intf:
      ngb[af] = str(netaddr.IPNetwork(intf[af]).ip)
  return ngb

class BGP(Module):

  def augment_node_data(self,node,topology):
    if not "bgp" in node:
      return
    check_bgp_parameters(node)
    rrlist = find_bgp_rr(node.bgp.get("as"),topology)
    node.bgp.neighbors = []

    # If we don't have route reflectors, or if the current node is a route
    # reflector, we need BGP sessions to all other nodes in the same AS
    if not(rrlist) or node.bgp.get("rr",None):
      for n in topology.nodes:
        if "bgp" in n:
          if n.bgp.get("as") == node.bgp.get("as") and n.name != node.name:
            node.bgp.neighbors.append(bgp_neighbor(n,n.loopback))
    #
    # The node is not a route reflector, and we have a non-empty RR list
    # We need BGP sessions with the route reflectors
    else:
      for n in rrlist:
        if n.name != node.name:
          node.bgp.neighbors.append(bgp_neighbor(n,n.loopback))

    #
    # EBGP sessions - iterate over all links, find adjacent nodes
    # in different AS numbers, and create BGP neighbors
    for l in node.get("links",[]):
      for ngb_name,ngb_ifdata in l.get("neighbors",{}).items():
        neighbor = topology.nodes_map[ngb_name]
        if not "bgp" in neighbor:
          continue
        if neighbor.bgp.get("as") and neighbor.bgp.get("as") != node.bgp.get("as"):
          node.bgp.neighbors.append(bgp_neighbor(neighbor,ngb_ifdata))
