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

class PythonHandler : public BaseHandler
{
public:
    PythonHandler(pybind11::handle handler)
    : m_handler(handler)
    {
        m_enabled_for = osmium::osm_entity_bits::nothing;
        if (pybind11::hasattr(m_handler, "node")) {
            m_enabled_for |= osmium::osm_entity_bits::node;
        }
        if (pybind11::hasattr(m_handler, "way")) {
            m_enabled_for |= osmium::osm_entity_bits::way;
        }
        if (pybind11::hasattr(m_handler, "relation")) {
            m_enabled_for |= osmium::osm_entity_bits::relation;
        }
        if (pybind11::hasattr(m_handler, "area")) {
            m_enabled_for |= osmium::osm_entity_bits::area;
        }
        if (pybind11::hasattr(m_handler, "changeset")) {
            m_enabled_for |= osmium::osm_entity_bits::changeset;
        }
    }


    bool node(PyOSMNode &n) override
    {
        if (m_enabled_for & osmium::osm_entity_bits::node) {
            auto ret = m_handler.attr("node")(n.get_or_create_python_object());
            if (pybind11::isinstance<pybind11::bool_>(ret) && ret.cast<bool>()) {
                return true;
            }
        }
        return false;
    }

    bool way(PyOSMWay &w) override
    {
        if (m_enabled_for & osmium::osm_entity_bits::way) {
            auto ret = m_handler.attr("way")(w.get_or_create_python_object());
            if (pybind11::isinstance<pybind11::bool_>(ret) && ret.cast<bool>()) {
                return true;
            }
        }
        return false;
    }

    bool relation(PyOSMRelation &r) override
    {
        if (m_enabled_for & osmium::osm_entity_bits::relation) {
            auto ret = m_handler.attr("relation")(r.get_or_create_python_object());
            if (pybind11::isinstance<pybind11::bool_>(ret) && ret.cast<bool>()) {
                return true;
            }
        }
        return false;
    }

    bool changeset(PyOSMChangeset &c) override
    {
        if (m_enabled_for & osmium::osm_entity_bits::changeset) {
            auto ret = m_handler.attr("changeset")(c.get_or_create_python_object());
            if (pybind11::isinstance<pybind11::bool_>(ret) && ret.cast<bool>()) {
                return true;
            }
        }
        return false;
    }

    bool area(PyOSMArea &a) override
    {
        if (m_enabled_for & osmium::osm_entity_bits::area) {
            auto ret = m_handler.attr("area")(a.get_or_create_python_object());
            if (pybind11::isinstance<pybind11::bool_>(ret) && ret.cast<bool>()) {
                return true;
            }
        }
        return false;
    }
private:
    pybind11::handle m_handler;
};

} // namespace

#endif //PYOSMIUM_PYTHON_HANDLER_HPP

