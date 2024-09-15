# Input Formats and Other Sources

pyosmium can read OSM data from different sources and in different formats.

## Supported file formats

pyosmium has built-in support for the most common OSM data formats as well
as formats specific to libosmium. The format to use is usually determined by the
suffix of the file name. The following table gives an overview over the
suffix recognised, the corresponding format and if the formats support reading
and/or writing.

| Suffix         | Reading | Writing | Format |
|----------------|---------|---------|--------|
| `.pbf`         | :material-check: | :material-check: | protobuf-based PBF format |
| `.osm`         | :material-check: {: rowspan=2} | :material-check: {: rowspan=2} | Original XML format {: rowspan=2} |
| `.xml`         | &#8288 {: style="padding:0"}| &#8288 {: style="padding:0"}| &#8288 {: style="padding:0"} |
| `.o5m`         | :material-check: | :material-close: | Custom format created by the [osmc tools](https://wiki.openstreetmap.org/wiki/Osmfilter) |
| `.opl`         | :material-check: | :material-check: | Osmium's line based text format [OPL](https://osmcode.org/opl-file-format/) |
| `.debug`       | :material-close: | :material-check: | a verbose human-readable format |
| `.ids`         | :material-close: | :material-check: | Text format only containing the object IDs |

All formats also support compression with gzip (suffix `.gz`)
and bzip2 (suffix `.bz2`) with the exception of the PBF format.

The suffixes may be further prefixed by three subtypes:

* __`.osm`__ - A simple OSM data file.
  Each object appears at most with one version in the file.
* __`.osc`__ - An [OSM change file](08-Working-With-Change-Files.md).
  Multiple versions of an object may appear in the file. The file is
  usually not reference-complete.
* __`.osh`__ - An [OSM history file](09-Working-With-History-Files.md).
  Objects appear with all available versions in the file. The file is
  usually reference-complete.

Thus the type `.osh.xml.bz2` would be an OSM history file in XML format
that has been compressed using the bzip2 algorithm.

If you have file inputs where the suffix differs from the internal format,
the file type can be explicitly set by instantiating an [osmium.io.File][]
object. It takes an optional format parameter which then must contain
the suffix notation of the desired file format.

!!! example
    This example forces the given input text file to be read as OPL.

    ```python
    fp = osmium.FileProcessor(osmium.io.File('assorted.txt', 'opl'))
    ```

## Using standard input and output

The special file name `-` can be used to read from standard input or
write to standard output.

When reading data, use a `File` object to specify the file format. With
the SimpleReader, you need to use the parameter `filetype`.

!!! example
    This code snipped dumps all ids of your input file to the console.

    ```python
    with osmium.SimpleWriter('-', filetype='ids') as writer:
        for o in osmium.FileProcessor('test.pbf'):
            writer.add(o)
    ```

## Reading from buffers

pyosmium can also read data from a in-memory byte buffer. Simply wrap the
buffer in a [osmium.io.FileBuffer][]. The file format always needs to be
explicitly given.

!!! example
    Reading from a buffer comes in handy when loading OSM data from a URL.
    This example computes statistics over data downloaded from an URL.

    ```python
    import urllib.request as urlrequest

    data = urlrequest.urlopen('https://example.com/some.osm.gz').read()

    counter = {'n': 0, 'w': 0, 'r': 0}

    for o in osmium.FileProcessor(osmium.io.FileBuffer(data, 'osm.gz')):
        counter[o.type_str()] += 1

    print("Nodes: %d" % counter['n'])
    print("Ways: %d" % counter['w'])
    print("Relations: %d" % counter['r'])
    ```
