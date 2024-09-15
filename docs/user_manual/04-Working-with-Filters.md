# Pre-Filtering Input Data

When processing an OSM file, it is often only a very small part of the
objects the script really needs to see and process. Say, you are interested
in the road network, then the millions of buildings in the file could easily
be skipped over. This is the task of filters. They provide a fast and
performance-efficient way to pre-process or skip over data before it is
processed within the Python code.

## How filters work

Filters can be added to a FileProcessor with the
[`with_filter()`][osmium.FileProcessor.with_filter] function. An arbitrary
number of filters can be added to the processor. Simply call the functions
as many times as needed. The filters will be executed in the order they
have been added. If any of the filters marks the object for removal,
the object is immediately dropped and the next object from the file is
processed.

Filters can have side effects. That means that a filter may add additional
attributes to the OSM object it processes and these attributes will
be visible for subsequent filters and in the Python processing code.
For example, the GeoInterfaceFilter adds a Python `__geo_interface__`
attribute to the object.

Filters can be restricted to process only certain types of OSM objects.
If an OSM object doesn't have the right type, the filter will be skipped
over as if it wasn't defined at all. To restrict the types, call the
[`enable_for()`][osmium.BaseFilter.enable_for] function.

Here is an example of a FileProcessor where only place nodes and
boundary ways and relations are iterated through:

!!! example
    ```python
    fp = osmium.FileProcessor('../data/liechtenstein.osm.pbf')\
               .with_filter(osmium.filter.KeyFilter('place').enable_for(osmium.osm.NODE))\
               .with_filter(osmium.filter.KeyFilter('boundary').enable_for(osmium.osm.WAY | osmium.osm.RELATION))
    ```

## Fallback Processing

Once an object has been filtered, the default behaviour of the FileProcessor
is to simply drop the object. Sometimes it can be useful to do something
different with the object. For example, when you want to change some tags
in a file and then write the data out again, then you'd usually want to filter
out the objects that are not to be modified. However, you wouldn't want
to drop them completely but write the unmodified object out. For such cases
it is possible to set a fallback handler for filtered objects using the
[`handler_for_filtered()`][osmium.FileProcessor.handler_for_filtered] function.

The file writer can become a fallback handler for the file processor. The
[next chapter Handlers](05-Working-with-Handlers.md) will show how to write
a custom handler that can be used in this function.


## Built-in Filters

The following section shortly describes the filters that are built into pyosmium.

### EmptyTagFilter

This filter removes all objects that have no tags at all. Most of the nodes
in an OSM files fall under this category. So even when you don't want to
apply any other filters, this one can make a huge difference in processing time:

!!! example
    === "Code"
    ```python
    print("Total number of objects:",
          sum(1 for o in osmium.FileProcessor('liechtenstein.osm.pbf')))

    print("Total number of tagged objects:",
          sum(1 for o in osmium.FileProcessor('liechtenstein.osm.pbf')
                               .with_filter(osmium.filter.EmptyTagFilter())))
    ```
    === Output
    ```
    Total number of objects: 340175
    Total number of tagged objects: 49645
    ```


### EntityFilter

The Entity filter only lets through objects of the selected type:


!!! example
    === "Code"
    ```python
    print("Total number of objects:",
          sum(1 for o in osmium.FileProcessor('../data/liechtenstein.osm.pbf')))

    print("Of which are nodes:",
          sum(1 for o in osmium.FileProcessor('../data/liechtenstein.osm.pbf')
                               .with_filter(osmium.filter.EntityFilter(osmium.osm.NODE))))
    ```
    === "Output"
    ```
    Total number of objects: 340175
    Of which are nodes: 306700
    ```


On the surface, the filter is very similar to the entity selector that
can be passed to the FileProcessor. In fact, it would be much faster to count
the nodes using the entity selector:

!!! example
    ```python
    print("Of which are nodes:",
          sum(1 for o in osmium.FileProcessor('../data/liechtenstein.osm.pbf', osmium.osm.NODE)))
    ```
    === "Output"
    ```
    Of which are nodes: 306700
    ```


However, the two implementations use different mechanism to drop the nodes.
When the entity selector in the FileProcessor is used like in the second
example, then only the selected entities are read from the file. In our
example, the file reader would skip over the ways and relations completely.
When the entity filter is used, then the entities are only dropped when
they get to the filter. Most importantly, the objects will still be visible
to any filters applied _before_ the entity filter.

This can become of some importance when working with geometries. Lets say
we can to compute the length of all highways in our file. You will remember
from the last chapter about [Working with Geometries](03-Working-with-Geometries.md)
that it is necessary to enable the location cache in order to be able to
get the geometries of the road:

!!! example
    === "Code"
    ```python
    total = 0.0

    for o in osmium.FileProcessor('../data/liechtenstein.osm.pbf')\
        .with_locations()\
        .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY)):
        if 'highway' in o.tags:
            total += osmium.geom.haversine_distance(o.nodes)

    print(f'Total length of highways is {total/1000} km.')
    ```
    === "Output"
    ```
    Total length of highways is 1350.8030544343883 km.
    ```


The location cache needs to see all nodes in order to record their locations.
This would not happen if the file reader skips over the nodes. It is
therefore imperative to use the entity filter here. In fact, pyosmium will
refuse to run when nodes are not enabled in a FileProcessor with location
caching:

!!! bug "Bad example"
    === "Code"
    ```python
    for o in osmium.FileProcessor('../data/liechtenstein.osm.pbf', osmium.osm.WAY).with_locations():
        if 'highway' in o.tags:
            osmium.geom.haversine_distance(o.nodes)
    ```
    === "Output"
    ```
    ---------------------------------------------------------------------------

    RuntimeError                              Traceback (most recent call last)

    Cell In[14], line 1
    ----> 1 for o in osmium.FileProcessor('../data/liechtenstein.osm.pbf', osmium.osm.WAY).with_locations():
          2     if 'highway' in o.tags:
          3         osmium.geom.haversine_distance(o.nodes)


    File ~/osm/dev/pyosmium/build/lib.linux-x86_64-cpython-311/osmium/file_processor.py:46, in FileProcessor.with_locations(self, storage)
         42 """ Enable caching of node locations. This is necessary in order
         43     to get geometries for ways and relations.
         44 """
         45 if not (self._entities & osmium.osm.NODE):
    ---> 46     raise RuntimeError('Nodes not read from file. Cannot enable location cache.')
         47 if isinstance(storage, str):
         48     self._node_store = osmium.index.create_map(storage)


    RuntimeError: Nodes not read from file. Cannot enable location cache.
    ```


### KeyFilter

This filter only lets pass objects where its list of tags has any of the
keys given in the arguments of the filter.

If you want to ensure that all of the keys are present, use the
KeyFilter multiple times:

!!! example
    ```python
    print("Objects with 'building' _or_ 'amenity' key:",
          sum(1 for o in osmium.FileProcessor('../data/liechtenstein.osm.pbf')
                               .with_filter(osmium.filter.KeyFilter('building', 'amenity'))))

    print("Objects with 'building' _and_ 'amenity' key:",
          sum(1 for o in osmium.FileProcessor('../data/liechtenstein.osm.pbf')
                               .with_filter(osmium.filter.KeyFilter('building'))
                               .with_filter(osmium.filter.KeyFilter('amenity'))))
    ```

### TagFilter

This filter works exactly the same as the KeyFilter, only it looks for the
presence of whole tags (key and value) in the tag list of the object.

### IdFilter

This filter takes an iterable of numbers and lets only pass objects that
have an ID that matches the list. This filter is particularly useful when
doing a two-stage processing, where in the first stage the file is scanned
for objects that are of interest (for example, members of certain relations)
and then in the second stage these objects are read from the file. You
pretty much always want to use this filter in combination with the
`enable_for()` function to restrict it to a certain object type.

In its purest form, the filter could be used to search for a single object
in a file:

!!! example
```python
fp = osmium.FileProcessor('../data/buildings.opl')\
           .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))\
           .with_filter(osmium.filter.IdFilter([1]))

for o in fp:
    print(o)
```

However, in practise it is a very expensive way to find a single object.
Remember that the entire file will be scanned by the FileProcessor just
to find that one piece of information.

## Custom Python Filters

It is also possible to define a custom filter in Python. Most of the time
this is not very useful because calling a filter implemented in Python is
just as expensive as returning the OSM object to Python and doing the
processing then. However, it can be useful when the FileProcessor is
used as an Iterable input to other libraries like GeoPandas.

A Python filter needs to be implemented as a class that looks exactly
like a [Handler class](05-Working-with-Handlers.md): for each type that
should be handled by the filter, implement a callback function
`node()`, `way()`, `relation()`, `area()` or `changeset()`. If a callback
for a certain type is not implemented, then the object type will automatically
pass through the filter. The callback function needs to return either 'True',
when the object should be filtered out, or 'False' when it should pass through.

Here is a simple example of a filter that filters out all nodes that are older than 2020:

!!! example
    ```python
    import datetime as dt

    class DateFilter:

        def node(self, n):
            return n.timestamp < dt.datetime(2020, 1, 1, tzinfo=dt.UTC)


    print("Total number of objects:",
          sum(1 for o in osmium.FileProcessor('../data/liechtenstein.osm.pbf')))

    print("Without nodes older than 2020:",
          sum(1 for o in osmium.FileProcessor('../data/liechtenstein.osm.pbf')
                               .with_filter(DateFilter())))
    ```
