""" Provides some helper functions for test.
"""
import random
import tempfile
import os
import osmium

def _complete_object(o):
    """Takes a hash with an incomplete OSM object description and returns a
       complete one.
    """
    ret = { 'version' : '1', 'timestamp': "2012-05-01T15:06:20Z",
            'changeset' : "11470653", 'uid' : "122294", 'user' : "foo",
            'tags' : {}
          }
    ret.update(o)
    if ret['type'] == 'N':
        if 'lat' not in ret:
            ret['lat'] = random.random()*180 - 90
        if 'lon' not in ret:
            ret['lon'] = random.random()*360 - 180
    return ret

def _write_osm_obj(fd, obj):
    if obj['type'] == 'N':
        fd.write(('<node id="%(id)d" lat="%(lat).8f" lon="%(lon).8f" version="%(version)s" timestamp="%(timestamp)s" changeset="%(changeset)s" uid="%(uid)s" user="%(user)s"'% obj).encode('utf-8'))
        if obj['tags'] is None:
            fd.write('/>\n'.encode('utf-8'))
        else:
            fd.write('>\n'.encode('utf-8'))
            for k,v in iter(obj['tags'].items()):
                fd.write(('  <tag k="%s" v="%s"/>\n' % (k, v)).encode('utf-8'))
            fd.write('</node>\n'.encode('utf-8'))
    elif obj['type'] == 'W':
        fd.write(('<way id="%(id)d" version="%(version)s" changeset="%(changeset)s" timestamp="%(timestamp)s" user="%(user)s" uid="%(uid)s">\n' % obj).encode('utf-8'))
        for nd in obj['nodes']:
            fd.write(('<nd ref="%s" />\n' % (nd,)).encode('utf-8'))
        for k,v in iter(obj['tags'].items()):
            fd.write(('  <tag k="%s" v="%s"/>\n' % (k, v)).encode('utf-8'))
        fd.write('</way>\n'.encode('utf-8'))
    elif obj['type'] == 'R':
        fd.write(('<relation id="%(id)d" version="%(version)s" changeset="%(changeset)s" timestamp="%(timestamp)s" user="%(user)s" uid="%(uid)s">\n' % obj).encode('utf-8'))
        for mem in obj['members']:
            fd.write(('  <member type="%s" ref="%s" role="%s"/>\n' % mem).encode('utf-8'))
        for k,v in iter(obj['tags'].items()):
            fd.write(('  <tag k="%s" v="%s"/>\n' % (k, v)).encode('utf-8'))
        fd.write('</relation>\n'.encode('utf-8'))



def create_osm_file(data):
    """Creates a temporary osm XML file. The data is a list of OSM objects,
       each described by a hash of attributes. Most attributes are optional
       and will be filled with sensitive values, if missing. Mandatory are
       only `type` and `id`. For ways, nodes are obligatory and for relations
       the memberlist.
    """
    data.sort(key=lambda x:('NWR'.find(x['type']), x['id']))
    with tempfile.NamedTemporaryFile(dir='/tmp', suffix='.osm', delete=False) as fd:
        fname = fd.name
        fd.write("<?xml version='1.0' encoding='UTF-8'?>\n".encode('utf-8'))
        fd.write('<osm version="0.6" generator="test-pyosmium" timestamp="2014-08-26T20:22:02Z">\n'.encode('utf-8'))
        fd.write('\t<bounds minlat="-90" minlon="-180" maxlat="90" maxlon="180"/>\n'.encode('utf-8'))

        for obj in data:
            _write_osm_obj(fd, _complete_object(obj))

        fd.write('</osm>\n'.encode('utf-8'))

    return fname

def osmobj(kind, **args):
    ret = dict(args)
    ret['type'] = kind
    return ret


class HandlerTestBase:

    def test_func(self):
        fn = create_osm_file(self.data)
        try:
            rd = osmium.io.Reader(fn)
            osmium.apply(rd, self.Handler())
            rd.close()
        finally:
            os.remove(fn)

