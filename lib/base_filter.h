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
    bool node(osmium::Node const *n) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::node)
               && filter_node(n);
    }

    bool way(osmium::Way *n) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::way)
               && filter_way(n);
    }

    bool relation(osmium::Relation const *n) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::relation)
               && filter_relation(n);
    }

    bool area(osmium::Area const *n) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::area)
               && filter_area(n);
    }

    bool changeset(osmium::Changeset const *n) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::changeset)
               && filter_changeset(n);
    }

    BaseFilter *enable_for(osmium::osm_entity_bits::type entities)
    {
        m_enabled_for = entities;
        return this;
    }

protected:
    virtual bool filter(osmium::OSMObject const *) { return false; }
    virtual bool filter_node(osmium::Node const *n) { return filter(n); }
    virtual bool filter_way(osmium::Way const *w) { return filter(w); }
    virtual bool filter_relation(osmium::Relation const *r) { return filter(r); }
    virtual bool filter_area(osmium::Area const *a) { return filter(a); }
    virtual bool filter_changeset(osmium::Changeset const *) { return false; }

private:
    osmium::osm_entity_bits::type m_enabled_for = osmium::osm_entity_bits::all;

};


void init_empty_tag_filter(pybind11::module &m);
void init_key_filter(pybind11::module &m);

} // namespace


#endif //PYOSMIUM_BASE_FILTER_HPP
