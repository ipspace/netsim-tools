# BGP Configuration Module

The BGP configuration module configures BGP routing process and BGP neighbors.

### BGP Configuration Parameters

You can use these node-level parameters to influence the final BGP configuration:

* **bgp.as**: AS number -- specified on a node, or as default global value (propagated to all nodes without a specified AS number)
* **bgp.rr** -- the node is BGP route reflector within its autonomous system.
* **bgp.rr_list**: global list of route reflectors across all autonomous systems in the lab topology. This list is used solely as a convenient mechanism to set **bgp.rr** node attribute. See [IBGP example](bgp_example/ibgp.md) for details.
* **bgp.next_hop_self** -- use *next-hop-self* on IBGP sessions. Can be specified as a global value; system default is **true**.

You can also use these link-level parameters to influence the BGP prefix advertisements:

* **bgp.advertise** -- The link prefix will be configured with the **network** statement within the BGP process.

See [examples](#examples) for sample usage guidelines.

**Notes:**
* You *must* specify **bgp.as** parameter for every node using BGP configuration module. The default AS number could be specified as a global parameter. Explore [simple BGP example](bgp_example/simple.md) to see how you can combine global AS number with node AS number.
* A node is using BGP configuration module if you enable BGP globally (using **module: [ bgp ]** as a top-level topology element) or for a node (using **module: [ bgp ]** within node data).

### Advertised BGP Prefixes

The following IP prefixes are configured with **network** statements within the BGP routing process:

* Loopback interface IPv4 prefix (usually a /32)
* IPv4 prefixes from links with **bgp.advertise** parameter set to **true**.
* Prefixes assigned to *stub* networks -- links with a single node attached to them or links with **role** set to **stub**. To prevent a stub prefix from being advertised, set **bgp.advertise** link parameter to **false**

**Notes:**
* If you set **bgp.advertise** parameter on a link, all nodes connected to the link advertise the link prefix. In the following example, the link prefix is advertised by PE1 and PE2.

```
links:
...
- pe1:
  pe2:
  bgp:
    advertise: true
``` 

* If you set **bgp.advertise** parameter within a node connected to a link, only that node advertises the link prefix. In the following example, the link prefix is advertised just by PE1:

```
links:
...
- pe1:
    bgp:
      advertise: true
  pe2:
``` 

* You can change the default prefix advertisement rules with the  **defaults.bgp.advertise_roles** list. The system default value of that variable is **[ stub ]**. For example, to advertise LAN (multi-access) and stub prefixes, use the following setting:

```
defaults:
  bgp:
    advertise_roles: [ lan, stub ]
``` 


### BGP Sessions

The BGP transformation module builds a list of BGP neighbors for ever node. That list of neighbors is then used to configure BGP neighbors within the BGP routing process:

**IBGP sessions**
* If there are no route reflectors within an autonomous system (no device within the autonomous system has **bgp.rr** set to *true*), you'll get a full mesh of IBGP sessions.
* Router reflectors have IBGP sessions to all other nodes in the same AS. When the remote node is not a router reflector, *route-reflector-client* is configured on the IBGP session.
* Route reflector clients have IBGP sessions with route reflectors (nodes within the same AS with **bgp.rr** set).
* IBGP sessions are established between loopback interfaces. You should combine IGBP deployment with an IGP configuration module like [OSPF](ospf.md).

See the [IBGP Data Center Fabric](bgp_example/ibgp.md) example for more details.

**EBGP sessions**
* Whenever multiple nodes connected to the same link use different AS numbers, you'll get a full mesh of EBGP sessions between them.

See the [Simple BGP Example](bgp_example/simple.md) and [EBGP Data Center Fabric](bgp_example/ebgp.md) example for more details.

#### Notes on Unnumbered EBGP Sessions

Unnumbered EBGP sessions are supported by the data model, but not by configuration templates. The transformed data model includes **unnumbered** and **ifindex** elements on EBGP neighbors reachable over unnumbered interfaces -- compare a regular EBGP neighbor (L2) with an unnumbered EBGP neighbor (L1):

```
- bgp:
    as: 65001
    neighbors:
    - as: 65100
      ifindex: 1
      name: l1
      type: ebgp
      unnumbered: true
    - as: 65101
      ipv4: 172.16.0.1
      name: l2
      type: ebgp
```

The transformed data model gives you enough information to create Cumulus-style BGP neighbor statements.

### Interaction with IGP

BGP transformation module can set link *role* on links used for EBGP sessions. The link role (when not specified on the link itself) is set to the value of **defaults.bgp.ebgp_role** (default system value: **external**).

**Consequence:** default settings exclude links with EBGP sessions from IGP processes. See the [Simple BGP Example](bgp_example/simple.md) for details.

## Examples

```eval_rst
.. toctree::
   :maxdepth: 2

   bgp_example/simple.md
   bgp_example/ibgp.md
   bgp_example/ebgp.md
```
