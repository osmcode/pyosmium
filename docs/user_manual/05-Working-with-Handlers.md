# Handler-based Processing

All examples so far have used the FileProcessor for reading files. It provides
an iterative way of working through the data, which comes quite natural to
a Python programmer. This chapter shows a different way of processing a file.
It shows how to create one or more handler classes and apply those to
an input file.

_Note:_ handler classes used to be the only way of processing data in
older pyosimum versions. You may therefore find them in many tutorials
and examples. There is no disadvantage in using FileProcessors instead.
Handlers simply provide a different syntax for achieving a similar goal.

## The handler object and osmium.apply

A pyosmium handler object is simply a Python object that implements callbacks
to handle the different types of entities (`node`, `way`, `relation`, `area`,
`changeset`). Usually you would define a class with your handler functions
and instantiate it. A complete handler class that prints out each object
in the file would look like this:

!!! example
    ```python
    class PrintHandler:
        def node(self, n):
            print(n)

        def way(self, w):
            print(w)

        def relation(self, r):
            print(r)

        def area(self, a):
            print(a)

        def changeset(self, c):
            print(c)
    ```

Such a handler is applied to an OSM file with the function
[`osmium.apply()`][osmium.apply]. The function takes a single file as an
argument and then an arbitrary number of handlers:

!!! example
    === "Code"
    ```python
    import osmium

    my_handler = PrintHandler()

    osmium.apply('buildings.opl', my_handler)
    ```
    === "Output"
    ```
    n1: location=45.0000000/13.0000000 tags={}
    n2: location=45.0001000/13.0000000 tags={}
    n3: location=45.0001000/13.0001000 tags={}
    n4: location=45.0000000/13.0001000 tags={entrance=yes}
    n11: location=45.0000100/13.0000100 tags={}
    n12: location=45.0000500/13.0000100 tags={}
    n13: location=45.0000500/13.0000500 tags={}
    n14: location=45.0000100/13.0000500 tags={}
    w1: nodes=[1,2,3,4,1] tags={amenity=restaurant}
    w2: nodes=[11,12,13,14,11] tags={}
    r1: members=[w1,w2], tags={type=multipolygon,building=yes}
    ```

## Using filters with apply

[Filter functions](04-Working-with-Filters.md) are also recognised as handlers
by the apply functions. They have the same effect as when used in FileProcessors:
when they signal to filter out an object, then the processing is stopped for
that object and the next object is processed. You can arbitrarily mix filters
and custom-made handlers. They are sequentially executed in the order in which
they appear in the apply function:

!!! example
    ```python
    osmium.apply('buildings.opl',
                 osmium.filter.EntityFilter(osmium.osm.RELATION),
                 my_handler,
                 osmium.filter.KeyFilter('route')),
                 my_other_handler
    ```


## The `osmium.SimpleHandler` class

The `apply` function is a very low-level function for processing. It will
only apply the handler functions to the input and be done with it.
It will in particular not care about providing the necessary building blocks
for [geometry processing](03-Working-with-Geometries.md). If you need to
work with geometries, you can derive your handler class from 
[`osmium.SimpleHandler`][]. This mix-in class adds two convenience functions
to your handler : [`apply_file()`][osmium.SimpleHandler.apply_file]
and [`apply_buffer()`][osmium.SimpleHandler.apply_buffer].
These functions apply the handler itself to a file or buffer but come with
additional parameter to enable location. If the handler implements an `area`
callback, then they automatically enable area processing as well.
