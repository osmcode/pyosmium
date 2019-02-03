import typing

from .io import Reader, Writer
from .osm import Location, Node, Way, Relation, Area, Changeset, mutable


class InvalidLocationError(RuntimeError): ...


class NotFoundError(KeyError): ...


class MergeInputReader(Reader):
    def add_buffer(self, buffer, format: str) -> int: ...

    def add_file(self, file: str) -> int: ...

    def apply(self, handler: BaseHandler, idx: typing.Optional[str], simplify: bool = ...): ...

    def apply_to_reader(self, reader: Reader, writer: Writer, with_history: bool = ...): ...


LocationTable = typing.Mapping[int, Location]


class NodeLocationsForWays(LocationTable):
    def ignore_errors(self): ...


class BaseHandler:
    def node(self, node: Node): ...

    def way(self, way: Way): ...

    def relation(self, relation: Relation): ...

    def area(self, area: Area): ...

    def changeset(self, changeset: Changeset): ...

    def apply_start(self): ...


class SimpleHandler(BaseHandler):
    def apply_buffer(self, buffer: bytes, format: str, locations: bool = ..., idx: str = ...): ...

    def apply_file(self, filename: str, locations: bool = ..., idx: str = ...): ...


class SimpleWriter:
    def __init__(self, arg2: str, arg3: typing.Optional[int]): ...  # filename, buffer_size

    def add_node(self, node: typing.Union[Node, mutable.Node]): ...

    def add_relation(self, relation: typing.Union[Relation, mutable.Relation]): ...

    def add_way(self, way: typing.Union[Way, mutable.Way]): ...

    def close(self): ...


class WriteHandler(BaseHandler):
    def __init__(self, arg2: str, arg3: typing.Optional[int]): ...  # filename, buffer_size


@typing.overload
def apply(arg1: Reader, arg2: BaseHandler): ...  # reader, write_handler


@typing.overload
def apply(arg1: Reader, arg2: NodeLocationsForWays): ...  # reader, nodes_idx


@typing.overload
def apply(arg1: Reader, arg2: NodeLocationsForWays, arg3: BaseHandler): ...  # reader, nodes_idx, write_handler
