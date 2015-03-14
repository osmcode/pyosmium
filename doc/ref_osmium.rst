``osmium`` - Processing OSM files
---------------------------------

Osmium processes files by reading data from a file and applying them
to a processing chain. Pyosmium offers a simplified wrapper to this
interface with the ``SimpleHandler`` class from which an OSM file processor
can easily be derived.

For more fine grained control of the processing chain, the more basic
functions and processors are exported as well in this module.

Simple Handlers
^^^^^^^^^^^^^^^

.. autoclass:: osmium.SimpleHandler
    :members:
    :undoc-members:


Low-level Functions and Classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: osmium.apply
