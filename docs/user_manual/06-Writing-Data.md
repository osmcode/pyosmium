# Writing Data

pyosmium can also be used to write OSM files. It offers different writer
classes which support creating referentially correct files.

## Basic writer usage

All writers are created by instantiating them with the name of the file to
write to.

!!! example
    ```python
    writer = osmium.SimpleWriter('my_extra_data.osm.pbf')
    ```

The format of the output file is usually determined through the file prefix.
pyosmium will refuse to overwrite any existing files. Either make sure to
delete the files before instantiating a writer or use the parameter
`overwrite=true`.

All writers are [context managers](https://docs.python.org/3/reference/datamodel.html#context-managers) and to ensure that the file is properly closed in the
end, the recommended  way to use them is in a with statement:

!!! example
    ```python
    with osmium.SimpleWriter('my_extra_data.osm.pbf') as writer:
        # do stuff here
    ```

When not used inside a with block, then don't forget to call the `close()`
function explicitly to close the writer.

Once a writer is instantiated, one of the `add*` functions can be used to
add an OSM object to the file. You can either use one of the
`add_node/way/relation` functions to force writing a specific type of
object or use the generic `add` function, which will try to determine the
object type. The OSM objects are directly written out in the order in which
they are given to the writer object. It is your responsibility as a user to
make sure that the order is correct with respect to the
[conventions for object order][order-in-osm-files].

Here is a complete example for a script that converts a file from OPL format
to PBF format:

!!! example
    ```python
    with osmium.SimpleWriter('buildings.osm.pbf') as  writer:
        for o in osmium.FileProcessor('buildings.opl'):
            writer.add(o)
    ```

### Writing modified objects

In the example above an OSM object from an input file was written out directly
without modifications. Writers can accept OSM nodes, ways and relations
that way. However, usually you want to modify some of the data in the object
before writing it out again. Use the `replace()` function to create a
_mutable version_ of the object with the given parameters replaced.

Say you want to create a copy of a OSM file with all `source` tags removed:

!!! example
    ```python
    with osmium.SimpleWriter('buildings.osm.pbf') as  writer:
        for o in osmium.FileProcessor('buildings.opl'):
            if 'source' in tags:
                new_tags = dict(o.tags) # make a copy of the tags
                del new_tags['source']
                writer.add(o.replace(tags=new_tags))
            else:
                # No source tag. Write object out as-is.
                writer.add(o)
    ```

### Writing custom objects

You can also write data that is not based on OSM input data at all. The write
functions will accept any Python object that mimics the attributes of a
node, way or relation.

Here is a simple example that writes out four random points:

!!! example
    ``` python
    from random import uniform

    class RandomNode:
        def __init__(self, name, id):
            self.id = id
            self.location = (uniform(-180, 180), uniform(-90, 90))
            self.tags = {'name': name}

    with osmium.SimpleWriter('points.opl') as writer:
        for i in range(4):
            writer.add_node(RandomNode(f"Random {i}", i))
    ```

The following table gives an overview over the recognised attributes and
acceptable types. If an attribute is missing, then pyosmium will choose a
suitable default or leave the attribute out completely from the output if
that is possible.

| attribute | types |
|-----------|----------------------------|
| id        | `int` |
| version   | `int` (positive non-zero value) |
| visible   | `bool` |
| changeset | `int` (positive non-zero value) |
| timestamp | `str` or `datetime` (will be translated to UTC first) |
| uid       | `int` |
| tags      | [osmium.osm.TagList][], a dict-like object or a list of tuples, where each tuple contains a (key, value) string pair |
| user      | `str` |
| location  | _(node only)_ [osmium.osm.Location][] or a tuple of lon/lat coordinates |
| nodes     | _(way only)_ [osmium.osm.NodeRefList][] or a list consisting of either [osmium.osm.NodeRef][]s or simple node ids |
| members   | _(relation only)_ [osmium.osm.RelationMemberList][] or a list consisting of either [osmium.osm.RelationMember][]s or tuples of `(type, id, role)`. The member type must be a single character 'n', 'w' or 'r'. |

The `osmium.osm.mutable` module offers pure Python-object versions of `Node`,
`Way` and `Relation` to make the creation of custom objects easier. Any of
the allowable attributes may be set in the constructor. This makes the
example for writing random points a bit shorter:

!!! example
    ``` python
    from random import uniform

    with osmium.SimpleWriter('points.opl') as writer:
        for i in range(4):
            writer.add_node(osmium.osm.mutable.Node(
                id=i, location = (uniform(-180, 180), uniform(-90, 90)),
                tags={'name': f"Random {i}"}))
    ```


## Writer types

pyosmium implements three different writer classes: the basic
[SimpleWriter][osmium.SimpleWriter] and
the two reference-completing writers
[ForwardReferenceWriter][osmium.ForwardReferenceWriter] and
[BackReferenceWriter][osmium.BackReferenceWriter].

### Writing specific objects only

The [SimpleWriter][osmium.SimpleWriter] creates an OSM data file by directly
writing out any OSM object that it receives in the chosen format.


### Writing reference-complete files

The [BackReferenceWriter][osmium.BackReferenceWriter] will make sure that the
file that is written out is reference-complete, meaning all objects that are
directly referenced by the object written are added to the output file as well.
This is needed when you want to make sure that geometries can be recreated
from the object in the file.

Creating a file with backward references is a two-stage process: while the
writer is open, it will write all objects received through one of the `add_*()`
functions into a temporary file and keeps a record of which objects are needed
to make the file reference-complete. Once the writer is closed, it collects the
missing object from a given reference file, merges them with the data from
the temporary file and writes out the final result.

### Writing files with forward references

The [ForwardReferenceWriter][osmium.ForwardReferenceWriter] completes the
written objects with forward references. This is particularly useful when
creating geographic extracts of any kind: one selects the node of interest
in a particular area and then lets the ForwardReferenceWriter complete the
ways and relations referring to the nodes.

Files written by the ForwardReferenceWriter are not necessarily
reference-complete. That is easy to see when considering the example of the
geographic extract: there may be ways in the area that cross the boundary
of the area chosen but only the nodes within the area are written out. This
might be useful in many situations as the way would be simply seem to be cut
on the area of interest. However, it has the disadvantage that some objects
will get invalid geometries, especially when they represent areas.

The other thing to consider during forward completion are indirect references.
When completing relations indirectly referenced through ways or other relations,
then the resulting file can become big very quickly. For example, a seemingly
small extract of the city of Strasbourg can suddenly contain not only the
relations for France and Germany but also electoral boundaries and entire
timezones. For that reason, when forward-completing relations, it is not
recommended to use backward completion.
