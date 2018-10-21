import typing

from .io import Reader, Writer
from .osm import Node, Way, Relation, Area, Changeset, mutable
from .index import LocationTable


class InvalidLocationError(RuntimeError): ...


class NotFoundError(KeyError): ...


class MergeInputReader(Reader):
    def add_buffer(self, buffer: bytes, format: str) -> int: ...

    def add_file(self, file: str) -> int: ...

    def apply(self, handler: BaseHandler, idx: typing.Optional[str], simplify: bool = ...) -> None: ...

    def apply_to_reader(self, reader: Reader, writer: Writer, with_history: bool = ...) -> None: ...


class NodeLocationsForWays(LocationTable):
    def ignore_errors(self) -> None: ...


class BaseHandler:
    def node(self, node: Node) -> None: ...

    def way(self, way: Way) -> None: ...

    def relation(self, relation: Relation) -> None: ...

    def area(self, area: Area) -> None: ...

    def changeset(self, changeset: Changeset) -> None: ...

    def apply_start(self) -> None: ...


class SimpleHandler(BaseHandler):
    def apply_buffer(self, buffer: bytes, format: str, locations: bool = ..., idx: str = ...) -> None: ...

    def apply_file(self, filename: str, locations: bool = ..., idx: str = ...) -> None: ...


class SimpleWriter:
    def __init__(self, arg2: str, arg3: typing.Optional[int]) -> None: ...  # filename, buffer_size

    def add_node(self, node: typing.Union[Node, mutable.Node]) -> None: ...

    def add_relation(self, relation: typing.Union[Relation, mutable.Relation]) -> None: ...

    def add_way(self, way: typing.Union[Way, mutable.Way]) -> None: ...

    def close(self) -> None: ...


class WriteHandler(BaseHandler):
    def __init__(self, arg2: str, arg3: typing.Optional[int]): ...  # filename, buffer_size


@typing.overload
def apply(arg1: Reader, arg2: BaseHandler) -> None: ...  # reader, write_handler


@typing.overload
def apply(arg1: Reader, arg2: NodeLocationsForWays) -> None: ...  # reader, nodes_idx


@typing.overload
def apply(arg1: Reader, arg2: NodeLocationsForWays, arg3: BaseHandler) -> None: ...  # reader, nodes_idx, write_handler
