# SPDX-License-Identifier: BSD-2-Clause
#
# This file is part of pyosmium. (https://osmcode.org/pyosmium/)
#
# Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
# For a full list of authors see the git log.


def test_member_list_length(simple_handler):
    data = """\
           r2 Mn3@
           r4
           r45 Mw1@fo,r45@4,r45@5
           """

    rels = {}

    def cb(rel):
        rels[rel.id] = len(rel.members)

    simple_handler(data, relation=cb)

    assert rels == {2: 1, 4: 0, 45: 3}


def test_list_members(simple_handler):
    members = []

    def cb(rel):
        members.extend((m.type, m.ref, m.role) for m in rel.members)

    simple_handler("r34 Mn23@,n12@foo,w5@.,r34359737784@(ü)", relation=cb)

    assert members == [('n', 23, ''), ('n', 12, 'foo'), ('w', 5, '.'),
                       ('r', 34359737784, '(ü)')]
