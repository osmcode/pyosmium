/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#ifndef PYOSMIUM_BASE_FILTER_HPP
#define PYOSMIUM_BASE_FILTER_HPP

#include <osmium/osm.hpp>
#include <osmium/osm/entity_bits.hpp>

#include "base_handler.h"

namespace pyosmium {

class BaseFilter : public BaseHandler {
public:
    bool node(PyOSMNode &o) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::node)
               && filter_node(o);
    }

    bool way(PyOSMWay &o) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::way)
               && filter_way(o);
    }

    bool relation(PyOSMRelation &o) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::relation)
               && filter_relation(o);
    }

    bool area(PyOSMArea &o) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::area)
               && filter_area(o);
    }

    bool changeset(PyOSMChangeset &o) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::changeset)
               && filter_changeset(o);
    }

    BaseFilter *enable_for(osmium::osm_entity_bits::type entities)
    {
        m_enabled_for = entities;
        return this;
    }

protected:
    virtual bool filter(osmium::OSMObject const *) { return false; }

    virtual bool filter_node(PyOSMNode &o) { return filter(o.get()); }
    virtual bool filter_way(PyOSMWay &o) { return filter(o.get()); }
    virtual bool filter_relation(PyOSMRelation &o) { return filter(o.get()); }
    virtual bool filter_area(PyOSMArea &o) { return filter(o.get()); }
    virtual bool filter_changeset(PyOSMChangeset &o) { return false; }
};


void init_empty_tag_filter(pybind11::module &m);
void init_key_filter(pybind11::module &m);
void init_tag_filter(pybind11::module &m);
void init_id_filter(pybind11::module &m);
void init_entity_filter(pybind11::module &m);
void init_geo_interface_filter(pybind11::module &m);

} // namespace


#endif //PYOSMIUM_BASE_FILTER_HPP
