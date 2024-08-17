/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#ifndef PYOSMIUM_OSM_BASE_OBJECTS_HPP
#define PYOSMIUM_OSM_BASE_OBJECTS_HPP
#include <variant>

#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>

namespace pyosmium {

template <typename T>
class COSMDerivedObject
{
public:
    explicit COSMDerivedObject(T *obj) : m_obj(obj) {}

    T const *get() const {
        if (!m_obj) {
            throw std::runtime_error{"Illegal access to removed OSM object"};
        }
        return m_obj;
    }

    bool is_valid() const noexcept { return m_obj; }

    void invalidate() noexcept { m_obj = nullptr; }

private:
    T *m_obj;
};

using COSMNode = COSMDerivedObject<osmium::Node const>;
using COSMWay = COSMDerivedObject<osmium::Way const>;
using COSMRelation = COSMDerivedObject<osmium::Relation const>;
using COSMArea = COSMDerivedObject<osmium::Area const>;
using COSMChangeset = COSMDerivedObject<osmium::Changeset const>;

/**
 * Storage for a persistent Python object around a osmium object reference.
 *
 * This makes it possible to store additional information in the
 * Python object and carry it over between filters.
 */
template <typename T>
class PyOSMObject
{
public:
    explicit PyOSMObject(osmium::OSMEntity *obj)
    : m_obj(static_cast<T *>(obj)) {}

    ~PyOSMObject()
    {
        if (has_python_object()) {
            m_pyobj.attr("_pyosmium_data").template cast<COSMDerivedObject<T const> *>()->invalidate();
        }
    }

    bool has_python_object() const
    { return m_valid; }

    T *get() const
    { return m_obj; }


    // must be called with GIL acquired
    pybind11::object get_or_create_python_object()
    {
        if (!m_valid) {
            m_valid = true;
            if constexpr (std::is_same_v<T, osmium::Node>) {
                m_pyobj = pybind11::module_::import("osmium.osm.types").attr("Node")(COSMNode{m_obj});
            } else if constexpr (std::is_same_v<T, osmium::Way>) {
                m_pyobj = pybind11::module_::import("osmium.osm.types").attr("Way")(COSMWay{m_obj});
            } else if constexpr (std::is_same_v<T, osmium::Relation>) {
                m_pyobj = pybind11::module_::import("osmium.osm.types").attr("Relation")(COSMRelation{m_obj});
            } else if constexpr (std::is_same_v<T, osmium::Area>) {
                m_pyobj = pybind11::module_::import("osmium.osm.types").attr("Area")(COSMArea{m_obj});
            } else if constexpr (std::is_same_v<T, osmium::Changeset>) {
                m_pyobj = pybind11::module_::import("osmium.osm.types").attr("Changeset")(COSMChangeset{m_obj});
            }
        }

        return m_pyobj;
    }

private:
    T *m_obj;
    bool m_valid = false;
    pybind11::object m_pyobj;
};

using PyOSMNode = PyOSMObject<osmium::Node>;
using PyOSMWay = PyOSMObject<osmium::Way>;
using PyOSMRelation = PyOSMObject<osmium::Relation>;
using PyOSMArea = PyOSMObject<osmium::Area>;
using PyOSMChangeset = PyOSMObject<osmium::Changeset>;

using PyOSMAny = std::variant<bool, PyOSMNode, PyOSMWay, PyOSMRelation, PyOSMArea, PyOSMChangeset>;

} // namespace

#endif //PYOSMIUM_OSM_BASE_OBJECTS_HPP
