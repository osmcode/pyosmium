Updating OpenStreetMap data from change files
=============================================

OpenStreetMap is a database that is constantly extended and updated. When you
download the planet or an extract of it, you only get a snapshot of the
database at a given point in time. To keep up-to-date with the development
of OSM, you either need to download a new snapshot or you can update your
existing data from change files published along with the planet file.
Pyosmium ships with two tools that help you to process change files:
`pyosmium-get-changes` and `pyosmium-up-to-date`.

This section explains the basics of OSM change files and how to use Pyosmium's
tools to keep your data up to date.

About change files
------------------

Regular `change files <https://wiki.openstreetmap.org/wiki/Planet.osm/diffs>`_
are published for the planet and also by some extract services. These 
change files are special OSM data files containing all changes to the database
in a regular interval. Change files are not referentially complete. That means
that they only contain OSM objects that have changed but not necessarily
all the objects that are referenced by the changed objects. The result is
that change file are rarely useful on their own. But they can be used
to update an existing snapshot of OSM data.

Getting change files
--------------------

There are multiple sources for OSM change files available:

 * https://planet.openstreetmap.org/replication is the official source
   for planet-wide updates. There are change files for
   minutely, hourly and daily intervals available.

 * `Geofabrik <https://download.geofabrik.de>`_ offers daily change files
   for all its updates. See the extract page for a link to the replication URL.
   Note that change files go only about 3 months back. Older files are deleted.

 * download.openstreetmap.fr offers
   `minutely change files <https://download.openstreetmap.fr/replication/>`_
   for all its `extracts <https://download.openstreetmap.fr/extracts/>`_.

For other services also check out the list of providers on the
`OSM wiki <https://wiki.openstreetmap.org/wiki/Planet.osm>`_.

Updating a planet or extract
----------------------------

If you have downloaded the planet or an extract with a replication service,
then updating your OSM file can be as easy as::

  pyosmium-up-to-date <osmfile.osm.pbf>

This finds the right replication source and file to start with, downloads
changes and updates the given file with the data. You can repeat this command
whenever you want to have newer data. The command automatically picks up at
the same point where it left off after the previous update.

Choosing the replication source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OSM files in PBF format are able to save the replication source and the
current status on their own. If you want to switch the replication source
or have a file that does not have the information, you need to bootstrap
the update process and manually point `pyosmium-up-to-date` to the right
service::

  pyosmium-up-to-date --ignore-osmosis-headers --server <replication URL> <osmfile.osm.pbf>

`pyosmium-up-to-date` automatically finds the right sequence ID to use
by looking at the age of the data in your OSM file. It updates the file
and stores the new replication source in the file. The additional parameters
are then not necessary anymore for subsequent updates.

.. ATTENTION::
   Always use the PBF format to store your data. Other format do not support
   to save the replication information. pyosmium-up-to-date is still able to
   update these kind of files if you manually point to the replication server
   but the process is always more costly because it needs to find the right
   starting point for updates first.

Updating larger amounts of data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When used without any parameters, pyosmium downloads at a maximum about
1GB of changes. That corresponds to about 3 days of planet-wide changes.
You can increase the amount using the additional `--size` parameter::

  pyosmium-up-to-date --size=10000 planet.osm.pbf

This would download about 10GB or 30 days of change data. If your OSM data file is
older than that, downloading the full file anew is likely going to be faster.

`pyosmium-up-to-date` uses return codes to signal if it has downloaded all
available updates. A return code of 0 means that it has downloaded and
applied all available data. A return code of 1 indicates that it has applied
some updates but more are available.

A minimal script that updates a file until it is really up-to-date with the
replcaition source would look like this::

  status=1  # we wnat more data
  while [ $status -eq 1 ]; do
    pyosmium-up-to-date planet.osm.pbf
    # save the return code
    status=$?
  done

Creating change files for updating databases
--------------------------------------------

There are quite a few tools that can import OSM data into databases, for
example osm2pgsql, imposm or Nominatim. These tools often can use change files
to keep their database up-to-date. pyosmium can be used to create the appropriate
change files. This is slightly more involved than updating a file.

Preparing the state file
^^^^^^^^^^^^^^^^^^^^^^^^

Before downloading the updates, you need to find out, with which sequence
number to start. The easiest way to remember your current status is to save
the number in a file. Pyosmium can then read and update the file for you.

Method 1: Starting from the import file
"""""""""""""""""""""""""""""""""""""""

If you still have the OSM file you used to set up your database, then
create a state file as follows::

  pyosmium-get-changes -O <osmfile.osm.pbf> -f sequence.state -v

Note that there is no output file yet. This creates a new file `sequence.state`
with the sequence ID where updates should start and prints the URL of the
replication service to use.

Method 2: Starting from a date
""""""""""""""""""""""""""""""

If you do not have the original OSM file anymore, then a good strategy is to
look for the date of the newest node in the database to find the snapshot date
of your database. Find the highest node ID, then look up the date for version 1
on the OSM website. For example the date for node 2367234 can be found at
https://www.openstreetmap.org/api/0.6/node/23672341/1 Find and copy the
`timestamp` field. Then create a state file using this date::

  pyosmium-get-changes -D 2007-01-01T14:16:21Z -f sequence.state -v

Also here, this creates a new file `sequence.state` with the sequence ID where
updates should start and prints the URL of the replication service to use.

Creating a change file
^^^^^^^^^^^^^^^^^^^^^^

Now you can create change files using the state::

  pyosmium-get-changes --server <replication server> -f sequence.state -o newchange.osm.gz

This downloads the latest changes from the server, saves them in the file
`newchange.osm.gz` and updates your state file. `<replication server>` is the
URL that was printed, when you set up the state file. The parameter can be
omitted when you use minutely change files from openstreetmap.org.

`pyosmium-get-changes` loads only about 100MB worth of updates at once (about
8 hours of planet updates). If you want more, then add a `--size` parameter.

Continuously updating a database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`pyosmium-get-changes` emits special return codes that can be used to set
up a script that continuously fetches updates and applies them to a
database. The important error codes are:

 * 0 - changes successfully downloaded and new change file created
 * 3 - no new changes are available from the server

All other error codes indicate fatal errors.

A simple shell script can look like this::

  while true; do
    # get the next batch of changes
    pyosmium-get-changes -f sequence.state -o newchange.osm.gz
    # save the return code
    status=$?

    if [ $status -eq 0 ]; then
      # apply newchange.osm.gz here
      ....
    elif [ $status -eq 3 ]; then
      # No new data, so sleep for a bit
      sleep 60
    else
      echo "Fatal error, stopping updates."
      exit $status
  done
