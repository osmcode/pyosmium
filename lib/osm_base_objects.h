/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2023 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#ifndef PYOSMIUM_OSM_BASE_OBJECTS_HPP
#define PYOSMIUM_OSM_BASE_OBJECTS_HPP

#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>

template <typename T>
class COSMDerivedObject {
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


#endif //PYOSMIUM_OSM_BASE_OBJECTS_HPP
