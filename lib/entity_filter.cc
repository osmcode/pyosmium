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

class EntityFilter : public pyosmium::BaseFilter
{
public:
    EntityFilter(osmium::osm_entity_bits::type entities)
    : m_entities(entities)
    {}

    bool filter_node(pyosmium::PyOSMNode &) override
    { return !(m_entities & osmium::osm_entity_bits::node); }

    bool filter_way(pyosmium::PyOSMWay &) override
    { return !(m_entities & osmium::osm_entity_bits::way); }

    bool filter_relation(pyosmium::PyOSMRelation &) override
    { return !(m_entities & osmium::osm_entity_bits::relation); }

    bool filter_area(pyosmium::PyOSMArea &) override
    { return !(m_entities & osmium::osm_entity_bits::area); }

    bool filter_changeset(pyosmium::PyOSMChangeset &) override
    { return !(m_entities & osmium::osm_entity_bits::changeset); }


private:
    osmium::osm_entity_bits::type m_entities;
};

}

namespace pyosmium {

void init_entity_filter(pybind11::module &m)
{
    py::class_<EntityFilter, pyosmium::BaseFilter, BaseHandler>(m, "EntityFilter")
        .def(py::init<osmium::osm_entity_bits::type>())
    ;
}

} // namespace
