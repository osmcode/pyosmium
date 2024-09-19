``index`` - Data Stores
-----------------------

The ``index`` submodule provides efficient storage containers for
preprocessed OSM data.


Node Location Storage
^^^^^^^^^^^^^^^^^^^^^

Node location can be cached in a ``LocationTable``. There are different
implementations available which should be choosen according to the size of
data and whether or not the cache should be permanent. See the Osmium manual
for a detailed explaination. The compiled in types can be listed with the
``map_types`` function, new stores can be created with ``create_map``.

.. autofunction:: osmium.index.map_types

.. autofunction:: osmium.index.create_map

.. autoclass:: osmium.index.LocationTable
    :members:
    :undoc-members:
