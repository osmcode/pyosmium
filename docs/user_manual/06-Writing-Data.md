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

Once a writer is instantiated, one of the `add*` functions can be used to
add an OSM object to the file. You can either use one of the
`add_node/way/relation` functions to force writing a specific type of
object or use the generic `add` function, which will try to determine the
object type. The OSM objects are directly written out in the order in which
they are given to the writer object. It is your responsibility as a user to
make sure that the order is correct with respect to the
[conventions for object order][order-in-osm-files].

After writing all data the writer needs to be closed using the `close()`
function. It is usually easier to use a writer as a context manager.

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

## Writer types

pyosmium implements three different writer classes: the basic
[SimpleWriter][osmium.SimpleWriter] and
the two reference-completing writers
[ForwardReferenceWriter][osmium.ForwardReferenceWriter] and
[BackReferenceWriter][osmium.BackReferenceWriter].
