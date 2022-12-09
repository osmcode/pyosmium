
from osmium.osm.mutable import create_mutable_node, create_mutable_way, create_mutable_relation

from osmium.osm.types import (OSMObject as OSMObject,
                              Node as Node,
                              Way as Way,
                              Relation as Relation,
                              Area as Area,
                              Changeset as Changeset,
                              Tag as Tag,
                              TagList as TagList,
                              NodeRef as NodeRef,
                              NodeRefList as NodeRefList,
                              WayNodeList as WayNodeList,
                              OuterRing as OuterRing,
                              InnerRing as InnerRing,
                              RelationMember as RelationMember,
                              RelationMemberList as RelationMemberList)

from osmium.osm._osm import (Location as Location,
                             Box as Box,
                             osm_entity_bits as osm_entity_bits,
                             NOTHING as NOTHING,
                             NODE as NODE,
                             WAY as WAY,
                             RELATION as RELATION,
                             AREA as AREA,
                             OBJECT as OBJECT,
                             CHANGESET as CHANGESET,
                             ALL as ALL)

setattr(Location, '__repr__',
        lambda l: f'osmium.osm.Location(x={l.x!r}, y={l.y!r})'
                      if l.valid() else 'osmium.osm.Location()')
setattr(Location, '__str__',
        lambda l: f'{l.lon_without_check():.7f}/{l.lat_without_check():.7f}'
                      if l.valid() else 'invalid')

setattr(Box, '__repr__', lambda b: f"osmium.osm.Box(bottom_left={b.bottom_left!r}, top_right={b.top_right!r})")
setattr(Box, '__str__', lambda b: f'({b.bottom_left!s} {b.top_right!s})')

