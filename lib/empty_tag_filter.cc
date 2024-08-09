/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>

#include "base_filter.h"

namespace py = pybind11;

namespace {

class EmptyTagFilter : public pyosmium::BaseFilter
{
    bool filter(osmium::OSMObject const *o) override
    {
        return o->tags().empty();
    }

    bool filter_changeset(pyosmium::PyOSMChangeset &o) override
    {
        return o.get()->tags().empty();
    }

};

} // namespace

namespace pyosmium {

void init_empty_tag_filter(pybind11::module &m)
{
    py::class_<EmptyTagFilter, pyosmium::BaseFilter, BaseHandler>(m, "EmptyTagFilter")
        .def(py::init<>())
    ;
}

} // namespace
