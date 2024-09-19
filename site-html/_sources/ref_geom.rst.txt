``geom`` - Geometry Helper Functions
------------------------------------

This module provides various helper functions for geometry handling.
Note: remember to apply a location handler before in order to use these geometry utilities on node locations.

Geometry Factories
^^^^^^^^^^^^^^^^^^

.. autoclass:: osmium.geom.WKBFactory
    :members:
    :undoc-members:

.. autoclass:: osmium.geom.WKTFactory
    :members:
    :undoc-members:

.. autoclass:: osmium.geom.GeoJSONFactory
    :members:
    :undoc-members:


Other Functions
^^^^^^^^^^^^^^^

.. autofunction:: osmium.geom.haversine_distance
