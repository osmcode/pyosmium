Troubleshooting
===============

``RuntimeError: callback keeps reference to OSM object``
--------------------------------------------------------

One of your callbacks tries to store the OSM object outside the scope of
the function. This is not allowed because for performance reasons, Osmium
gives you only a temporary view of the data. You must make a (deep) copy of all
data that you want to use later outside of the callback. See also
:ref:`intro-copying-data-from-object`.

Segfault when importing another library
---------------------------------------

There have been cases reported where pyosmium does not play well with other
python libraries that are compiled. If you see a segmentation fault when
importing pyosmium together with other libraries, try installing the
source code version of pyosmium. This can be done with pip::

    pip install --no-binary :all: osmium

You need to first install the depencies listed in the README.

