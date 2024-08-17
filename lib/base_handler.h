/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#ifndef PYOSMIUM_BASE_HANDLER_HPP
#define PYOSMIUM_BASE_HANDLER_HPP

#include <osmium/osm/entity.hpp>
#include <osmium/io/reader.hpp>

#include "osm_base_objects.h"

namespace pyosmium {

class BaseHandler
{
public:
    virtual ~BaseHandler() = default;

    // Actual handler functions.
    // All object handlers return a boolean which indicates if
    // processing is finished (true) or should be continued with the next
    // handler (false).
    virtual bool node(PyOSMNode &) { return false; }
    virtual bool way(PyOSMWay &) { return false; }
    virtual bool relation(PyOSMRelation &) { return false; }
    virtual bool area(PyOSMArea &)  { return false; }
    virtual bool changeset(PyOSMChangeset &) { return false; }

    virtual void flush() {}

    bool is_enabled_for(osmium::osm_entity_bits::type types) const
    {
        return types & m_enabled_for;
    }

protected:
    osmium::osm_entity_bits::type m_enabled_for = osmium::osm_entity_bits::all;
};

void apply(osmium::io::Reader &reader, BaseHandler &handler);
void apply_item(osmium::OSMEntity &item, BaseHandler &handler);

} // namespace

#endif // PYOSMIUM_BASE_HANDLER_HPP
