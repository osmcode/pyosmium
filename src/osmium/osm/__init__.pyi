from typing import Any

from . import mutable
from ._osm import *


def create_mutable_node(node: Node, **args: Any) -> mutable.Node: ...


def create_mutable_way(way: Way, **args: Any) -> mutable.Way: ...


def create_mutable_relation(rel: Relation, **args: Any) -> mutable.Relation: ...
