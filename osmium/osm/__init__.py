from ._osm import *
import osmium.osm.mutable

def create_mutable_node(node, **args):
    """ Create a mutable node replacing the properties given in the
        named parameters. Note that this function only creates a shallow
        copy which is still bound to the scope of the original object.
    """
    return osmium.osm.mutable.Node(base=node, **args)

def create_mutable_way(way, **args):
    """ Create a mutable way replacing the properties given in the
        named parameters. Note that this function only creates a shallow
        copy which is still bound to the scope of the original object.
    """
    return osmium.osm.mutable.Way(base=way, **args)

def create_mutable_relation(rel, **args):
    """ Create a mutable relation replacing the properties given in the
        named parameters. Note that this function only creates a shallow
        copy which is still bound to the scope of the original object.
    """
    return osmium.osm.mutable.Relation(base=rel, **args)

Node.replace = create_mutable_node
Way.replace = create_mutable_way
Relation.replace = create_mutable_relation
