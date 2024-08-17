/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <osmium/index/id_set.hpp>

#include "base_filter.h"

namespace py = pybind11;

namespace {

using IdSet = osmium::index::IdSetDense<osmium::unsigned_object_id_type>;

class IdFilter : public pyosmium::BaseFilter
{
public:
    IdFilter(py::iterable const &ids)
    {
        for (auto &i: py::iter(ids)) {
            m_ids.set(i.cast<osmium::unsigned_object_id_type>());
        }
    }

    bool filter(osmium::OSMObject const *o) override
    {
        return !m_ids.get(o->id());
    }

    bool filter_changeset(pyosmium::PyOSMChangeset &o) override
    {
        return !m_ids.get(o.get()->id());
    }

private:
    IdSet m_ids;
};

} // namespace

namespace pyosmium {

void init_id_filter(pybind11::module &m)
{
    py::class_<IdFilter, pyosmium::BaseFilter, pyosmium::BaseHandler>(m, "IdFilter")
        .def(py::init<py::iterable const &>())
    ;
}

} // namespace
