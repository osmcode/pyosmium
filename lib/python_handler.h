/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#ifndef PYOSMIUM_PYTHON_HANDLER_HPP
#define PYOSMIUM_PYTHON_HANDLER_HPP

#include <pybind11/pybind11.h>

#include "base_handler.h"
#include "osm_base_objects.h"

namespace pyosmium {

template <typename T>
class ObjectGuard {
    using WardPtr = T*;

    public:
        ObjectGuard(pybind11::object ward) : m_ward(ward) {}

        ~ObjectGuard() {
            m_ward.attr("_pyosmium_data").template cast<WardPtr>()->invalidate();
        }

    private:
        pybind11::object m_ward;
};


class PythonHandler : public BaseHandler
{
public:
    PythonHandler(pybind11::handle handler)
    : m_handler(std::move(handler))
    {
        m_enabled = osmium::osm_entity_bits::nothing;
        if (pybind11::hasattr(m_handler, "node")) {
            m_enabled |= osmium::osm_entity_bits::node;
        }
        if (pybind11::hasattr(m_handler, "way")) {
            m_enabled |= osmium::osm_entity_bits::way;
        }
        if (pybind11::hasattr(m_handler, "relation")) {
            m_enabled |= osmium::osm_entity_bits::relation;
        }
        if (pybind11::hasattr(m_handler, "area")) {
            m_enabled |= osmium::osm_entity_bits::area;
        }
        if (pybind11::hasattr(m_handler, "changeset")) {
            m_enabled |= osmium::osm_entity_bits::changeset;
        }
    }


    bool node(osmium::Node const *n) override
    {
        if (m_enabled & osmium::osm_entity_bits::node) {
            pybind11::gil_scoped_acquire acquire;
            auto obj = m_type_module.attr("Node")(COSMNode{n});
            ObjectGuard<COSMNode> guard(obj);
            m_handler.attr("node")(obj);
        }
        return false;
    }

    bool way(osmium::Way *w) override
    {
        if (m_enabled & osmium::osm_entity_bits::way) {
            pybind11::gil_scoped_acquire acquire;
            auto obj = m_type_module.attr("Way")(COSMWay{w});
            ObjectGuard<COSMWay> guard(obj);
            m_handler.attr("way")(obj);
        }
        return false;
    }

    bool relation(osmium::Relation const *r) override
    {
        if (m_enabled & osmium::osm_entity_bits::relation) {
            pybind11::gil_scoped_acquire acquire;
            auto obj = m_type_module.attr("Relation")(COSMRelation{r});
            ObjectGuard<COSMRelation> guard(obj);
            m_handler.attr("relation")(obj);
        }
        return false;
    }

    bool changeset(osmium::Changeset const *c) override
    {
        if (m_enabled & osmium::osm_entity_bits::changeset) {
            pybind11::gil_scoped_acquire acquire;
            auto obj = m_type_module.attr("Changeset")(COSMChangeset{c});
            ObjectGuard<COSMChangeset> guard(obj);
            m_handler.attr("changeset")(obj);
        }
        return false;
    }

    bool area(osmium::Area const *a) override
    {
        if (m_enabled & osmium::osm_entity_bits::area) {
            pybind11::gil_scoped_acquire acquire;
            auto obj = m_type_module.attr("Area")(COSMArea{a});
            ObjectGuard<COSMArea> guard(obj);
            m_handler.attr("area")(obj);
        }
        return false;
    }
private:
    osmium::osm_entity_bits::type m_enabled;
    pybind11::object m_type_module = pybind11::module_::import("osmium.osm.types");
    pybind11::handle m_handler;
};

} // namespace

#endif //PYOSMIUM_PYTHON_HANDLER_HPP

