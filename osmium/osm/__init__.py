from ._osm import *
import osmium.osm.mutable

def create_mutable_node(node, **args):
    return osmium.osm.mutable.Node(base=node, **args)

def create_mutable_way(node, **args):
    return osmium.osm.mutable.Way(base=node, **args)

def create_mutable_relation(node, **args):
    return osmium.osm.mutable.Relation(base=node, **args)

Node.replace = create_mutable_node
Way.replace = create_mutable_way
Relation.replace = create_mutable_relation
