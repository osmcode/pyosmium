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
               && (filter_node(n) != m_inverted);
    }

    bool way(osmium::Way *n) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::way)
               && (filter_way(n) != m_inverted);
    }

    bool relation(osmium::Relation const *n) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::relation)
               && (filter_relation(n) != m_inverted);
    }

    bool area(osmium::Area const *n) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::area)
               && (filter_area(n) != m_inverted);
    }

    bool changeset(osmium::Changeset const *n) override
    {
        return (m_enabled_for & osmium::osm_entity_bits::changeset)
               && (filter_changeset(n) != m_inverted);
    }

    BaseFilter *enable_for(osmium::osm_entity_bits::type entities)
    {
        m_enabled_for = entities;
        return this;
    }

    BaseFilter *invert(bool new_state)
    {
        m_inverted = new_state;
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
    bool m_inverted = false;
    osmium::osm_entity_bits::type m_enabled_for = osmium::osm_entity_bits::all;

};


void init_empty_tag_filter(pybind11::module &m);
void init_key_filter(pybind11::module &m);

} // namespace


#endif //PYOSMIUM_BASE_FILTER_HPP
