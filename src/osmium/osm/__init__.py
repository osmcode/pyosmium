
#from osmium.osm.mutable import create_mutable_node, create_mutable_way, create_mutable_relation

from osmium.osm.types import (Node as Node,
                              Way as Way,
                              Relation as Relation,
                              Area as Area,
                              Changeset as Changeset)

from osmium.osm._osm import (Location as Location)

setattr(Location, '__repr__',
        lambda l: f'osmium.osm.Location(x={l.x!r}, y={l.y!r})'
                      if l.valid() else 'osmium.osm.Location()')
setattr(Location, '__str__',
        lambda l: f'{l.lon_without_check():.7f}/{l.lat_without_check():.7f}'
                      if l.valid() else 'invalid')

