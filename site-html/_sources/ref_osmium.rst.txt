``osmium`` - Processing OSM files
---------------------------------

Osmium processes files by reading data from a file and applying them
to a processing chain. Pyosmium offers a simplified wrapper to this
interface with the ``SimpleHandler`` class from which an OSM file processor
can easily be derived.

For more fine grained control of the processing chain, the more basic
functions and processors are exported as well in this module.

Input Handlers
^^^^^^^^^^^^^^

An input handler provides the base class for writing custom
data processors. They take input data, usually from a file, and forward
it to handler functions.

.. autoclass:: osmium.SimpleHandler
    :members:
    :undoc-members:

SimpleWriter
^^^^^^^^^^^^

The writer class can be used to create an OSM file. The writer is able to
handle native ``osmium.osm`` objects as well as any Python object that
exposes the same attributes. It is not necessary to implement the full
list of attributes as any missing attributes will be replaced with a
sensible default value when writing. See :ref:`mutable-objects`
for a detailed discussion of the data formats understood for each attribute.

.. warning::

   Writers are considerably faster in handling native osmium data types than
   Python objects. You should therefore avoid converting objects whereever
   possible. This is not only true for the OSM data types like Node, Way and
   Relation but also for tag lists, node lists and member lists.

.. autoclass:: osmium.SimpleWriter
    :members:
    :undoc-members:

Low-level Functions and Classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: osmium.apply

.. autofunction:: osmium.make_simple_handler
