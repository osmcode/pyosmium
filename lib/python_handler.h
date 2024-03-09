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
    {}

    void node(osmium::Node const *n) override
    {
        pybind11::gil_scoped_acquire acquire;
        if (pybind11::hasattr(m_handler, "node")) {
            auto obj = m_type_module.attr("Node")(COSMNode{n});
            ObjectGuard<COSMNode> guard(obj);
            m_handler.attr("node")(obj);
        }
    }

    void way(osmium::Way *w) override
    {
        pybind11::gil_scoped_acquire acquire;
        if (pybind11::hasattr(m_handler, "way")) {
            auto obj = m_type_module.attr("Way")(COSMWay{w});
            ObjectGuard<COSMWay> guard(obj);
            m_handler.attr("way")(obj);
        }
    }

    void relation(osmium::Relation const *r) override
    {
        pybind11::gil_scoped_acquire acquire;
        if (pybind11::hasattr(m_handler, "relation")) {
            auto obj = m_type_module.attr("Relation")(COSMRelation{r});
            ObjectGuard<COSMRelation> guard(obj);
            m_handler.attr("relation")(obj);
        }
    }

    void changeset(osmium::Changeset const *c) override
    {
        pybind11::gil_scoped_acquire acquire;
        if (pybind11::hasattr(m_handler, "changeset")) {
            auto obj = m_type_module.attr("Changeset")(COSMChangeset{c});
            ObjectGuard<COSMChangeset> guard(obj);
            m_handler.attr("changeset")(obj);
        }
    }

    void area(osmium::Area const *a) override
    {
        pybind11::gil_scoped_acquire acquire;
        if (pybind11::hasattr(m_handler, "area")) {
            auto obj = m_type_module.attr("Area")(COSMArea{a});
            ObjectGuard<COSMArea> guard(obj);
            m_handler.attr("area")(obj);
        }
    }
private:
    pybind11::object m_type_module = pybind11::module_::import("osmium.osm.types");
    pybind11::handle m_handler;
};

} // namespace

#endif //PYOSMIUM_PYTHON_HANDLER_HPP

