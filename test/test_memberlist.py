# vim: set fileencoding=utf-8 :
from helpers import create_osm_file, osmobj, HandlerTestBase, check_repr

import osmium as o

class TestLength(HandlerTestBase):
    data = """\
           r2 Mn3@
           r4
           r45 Mw1@fo,r45@4,r45@5
           """

    class Handler(o.SimpleHandler):
        expected_length = { 2 : 1, 4 : 0, 45 : 3 }

        def relation(self, r):
            assert self.expected_length[r.id] == len(r.members)

class TestMembers(HandlerTestBase):
    data = u"""r34 Mn23@,n12@foo,w5@.,r34359737784@(ü)"""

    class Handler(o.SimpleHandler):

        def relation(self, r):
            m = list(r.members)
            assert 4 == len(m)
            assert 23 == m[0].ref
            assert 'n' == m[0].type
            assert '' == m[0].role
            assert 12 == m[1].ref
            assert 'n' == m[1].type
            assert 'foo' == m[1].role
            assert 5 == m[2].ref
            assert 'w' == m[2].type
            assert '.' == m[2].role
            assert 34359737784 == m[3].ref
            assert 'r' == m[3].type
            assert u'(ü)' == m[3].role
            assert check_repr(m)
