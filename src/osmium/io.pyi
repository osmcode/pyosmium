import typing

from .osm import Box

osm_entity_bits = typing.NewType(int)


class Header:
    has_multiple_object_versions: bool

    def box(self) -> Box: ...

    def get(self, key: str, default: typing.Optional[str]) -> str: ...

    def set(self, key: str, value: str): ...


class Reader:
    @typing.overload
    def __init__(self, arg2: str): ...

    @typing.overload
    def __init__(self, arg2: str, arg3: osm_entity_bits): ...

    def close(self): ...

    def eof(self) -> bool: ...

    def header(self) -> Header: ...


class Writer:
    @typing.overload
    def __init__(self, arg2: str): ...

    @typing.overload
    def __init__(self, arg2: str, arg3: Header): ...

    def close(self): ...
