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

def bgp_neighbor(n,intf,ctype,remote_rr):
  ngb = Box({},default_box=True,box_dots=True)
  ngb.name = n.name
  ngb["as"] = n.bgp.get("as")
  ngb["type"] = ctype
  if remote_rr:
    ngb.rr = True
  for af in ['ipv4','ipv6']:
    if af in intf:
      ngb[af] = str(netaddr.IPNetwork(intf[af]).ip)
  return ngb

class BGP(Module):

  def node_post_transform(self,node,topology):
    if not "bgp" in node:
      common.error("Node %s has BGP module enabled but no BGP parameters" % node.name)
    check_bgp_parameters(node)
    rrlist = find_bgp_rr(node.bgp.get("as"),topology)
    node.bgp.neighbors = []

    # If we don't have route reflectors, or if the current node is a route
    # reflector, we need BGP sessions to all other nodes in the same AS
    if not(rrlist) or node.bgp.get("rr",None):
      for n in topology.nodes:
        if "bgp" in n:
          if n.bgp.get("as") == node.bgp.get("as") and n.name != node.name:
            node.bgp.neighbors.append(bgp_neighbor(n,n.loopback,'ibgp',n.bgp.get("rr")))
    #
    # The node is not a route reflector, and we have a non-empty RR list
    # We need BGP sessions with the route reflectors
    else:
      for n in rrlist:
        if n.name != node.name:
          node.bgp.neighbors.append(bgp_neighbor(n,n.loopback,'ibgp',True))

    #
    # EBGP sessions - iterate over all links, find adjacent nodes
    # in different AS numbers, and create BGP neighbors
    for l in node.get("links",[]):
      for ngb_name,ngb_ifdata in l.get("neighbors",{}).items():
        neighbor = topology.nodes_map[ngb_name]
        if not "bgp" in neighbor:
          continue
        if neighbor.bgp.get("as") and neighbor.bgp.get("as") != node.bgp.get("as"):
          node.bgp.neighbors.append(bgp_neighbor(neighbor,ngb_ifdata,'ebgp',None))

  """
  Set link role based on BGP nodes attached to the link.

  If the nodes belong to at least two autonomous systems, and the ebgp_role
  variable is set, set the link role to ebgp_role
  """
  def link_pre_transform(self,link,topology):
    ebgp_role = topology.bgp.get("ebgp_role",None) or topology.defaults.bgp.get("ebgp_role",None)
    if not ebgp_role:
      return

    as_set = {}
    for n in link.keys():
      if n in topology.nodes_map:
        if "bgp" in topology.nodes_map[n]:
          node_as = topology.nodes_map[n].bgp.get("as")
        as_set[node_as] = True

    if len(as_set) > 1 and not link.get("role"):
      link.role = ebgp_role
