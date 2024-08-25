# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.
from typing import ClassVar, Union

from typing import overload
import osmium.osm
ALL: use_nodes
BACKWARD: direction
FORWARD: direction
UNIQUE: use_nodes

PointLike = Union[osmium.osm.Node, osmium.osm.Location, osmium.osm.NodeRef]
LineStringLike = Union[osmium.osm.Way, osmium.osm.WayNodeList]

class use_nodes:
    ALL: ClassVar[use_nodes] = ...
    UNIQUE: ClassVar[use_nodes] = ...
    def __init__(self, value: int) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class direction:
    BACKWARD: ClassVar[direction] = ...
    FORWARD: ClassVar[direction] = ...
    def __init__(self, value: int) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class Coordinates:
    """ Represent a x/y coordinate. The projection of the coordinate
        is left to the interpretation of the caller.
    """
    @overload
    def __init__(self) -> None:
        """ Create an invalid coordinate.
        """
    @overload
    def __init__(self, cx: float, cy: float) -> None:
        """ Create a coordinate with the given x and y values.
        """
    @overload
    def __init__(self, location: osmium.osm.Location) -> None:
        """ Create a coordinate from a node location.
        """
    def valid(self) -> bool:
        """ Return true if the coordinate is valid.
            A coordinate can only be invalid when both x and y are NaN.
        """
    @property
    def x(self) -> float:
        """ x portion of the coordinate.
        """
    @property
    def y(self) -> float:
        """ y portion of the coordinate.
        """

class FactoryProtocol:
    """ Protocol for classes that implement the necessary functions
        for converting OSM objects into simple-feature-like geometries.
    """
    def create_linestring(self, line: LineStringLike, use_nodes: use_nodes = ..., direction: direction = ...) -> str:
        """ Create a line string geometry from a way like object. This may be a
            [Way][osmium.osm.Way] or a [WayNodeList][osmium.osm.WayNodeList].
            Subsequent nodes with the exact same coordinates will be filtered
            out because many tools consider repeated coordinates in a
            line string invalid. Set _use_nodes_ to `osmium.geom.ALL` to
            suppress this behaviour.

            The line string usually follows the order of the node list.
            Set _direction_ to `osmium.geom.BACKWARDS` to inverse the direction.
        """
    def create_multipolygon(self, area: osmium.osm.Area) -> str:
        """ Create a multi-polygon geometry from an [Area][osmium.osm.Area]
            object.
        """
    def create_point(self, location: PointLike) -> str:
        """ Create a point geometry from a [Node][osmium.osm.Node], a
            location or a node reference.
        """
    @property
    def epsg(self) -> int:
        """ Projection of the output geometries as a EPSG number.
        """
    @property
    def proj_string(self) -> str:
        """ Projection of the output geometries as a projection string.
        """

class GeoJSONFactory(FactoryProtocol):
    """ Factory that creates GeoJSON geometries from osmium geometries.
    """

class WKBFactory(FactoryProtocol):
    """ Factory that creates WKB from osmium geometries.
    """

class WKTFactory(FactoryProtocol):
    """ Factory that creates WKT from osmium geometries.
    """

@overload
def haversine_distance(list: osmium.osm.WayNodeList) -> float:
    """ Compute the length of a way using the Haversine algorithm. It
        takes the curvature of earth into account.
    """
@overload
def haversine_distance(c1: Union[Coordinates, osmium.osm.Location],
                       c2: Union[Coordinates, osmium.osm.Location]) -> float:
    """ Compute the distance between two locations using the Haversine
        algorithm. It takes the curvature of earth into account. The
        coordinates must be in WGS84.
    """

def lonlat_to_mercator(coordinate: Coordinates) -> Coordinates:
    """ Convert coordinates from WGS84 to Mercator projection.
    """
def mercator_to_lonlat(coordinate: Coordinates) -> Coordinates:
    """ Convert coordinates from WGS84 to Mercator projection.
    """
