# IBGP Data Center Fabric

We want to create a leaf-and-spine fabric running IBGP on top of OSPF. The fabric will have two leafs (l1, l2) and two spines (s1, s2).

All devices run BGP and OSPF (we need OSPF within AS 65000 to propagate loopback interfaces):

```
module: [ bgp,ospf ]
```

Default BGP AS number is 65000. Default OSPF area is 0.0.0.0. Default device type is Cisco Nexus 9300v:

```
bgp:
  as: 65000
ospf:
  area: 0.0.0.0
defaults:
  device: nxos
```

Fabric point-to-point links are unnumbered:

```
addressing:
  p2p:
    unnumbered: true
```

The network topology has four nodes. One of the leafs is an Arista switch.

```
nodes:
  s1:
  s2:
  l1:
  l2:
    device: eos
```

The switches are linked in a leaf-and-spine fabric:

```
links:
- s1-l1
- s1-l2
- s2-l1
- s2-l2
```

We could use a full mesh of IBGP sessions, but it's more interesting to use spine switches as BGP route reflectors:

```
nodes:
  s1:
    bgp:
      rr: true 
  s2:
    bgp:
      rr: true 
  l1:
  l2:
    device: eos
```

### Resulting Device Configurations

The above topology generates the following device configurations (a single leaf and a single spine switch are shown):

#### S1 (Cisco NX-OS)

```
router ospf 1
!
interface Loopback0
 ip ospf 1 area 0.0.0.0
!
interface GigabitEthernet0/1
 ip ospf 1 area 0.0.0.0
 ip ospf network point-to-point
```

#### L2 (Arista EOS)

```
```

### Complete network topology:

```
#
# Simple BGP example (see documentation)
#
module: [ bgp,ospf ]

addressing:
  p2p:
    unnumbered: true

bgp:
  as: 65000
ospf:
  area: 0.0.0.0
defaults:
  device: nxos

nodes:
  s1:
    bgp:
      rr: true
  s2:
    bgp:
      rr: true
  l1:
  l2:
    device: eos

links:
- s1-l1
- s1-l2
- s2-l1
- s2-l2
```
