/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <algorithm>
#include <vector>

#include <pybind11/pybind11.h>

#include <osmium/osm/tag.hpp>
#include <osmium/geom/geojson.hpp>

#include "base_filter.h"

namespace {

class GeoInterfaceFilter : public pyosmium::BaseFilter
{
public:
    GeoInterfaceFilter(bool drop_invalid_geometries, pybind11::iterable const &tags)
    : m_drop_invalid_geometries(drop_invalid_geometries)
    {
        for (auto &t: pybind11::iter(tags)) {
            m_tags.push_back(t.cast<std::string>());
        }
    }

protected:
    bool filter_node(pyosmium::PyOSMNode &o) override
    {
        auto const &loc = o.get()->location();
        if (!loc.valid()) {
            return m_drop_invalid_geometries;
        }

        using namespace pybind11::literals;
        pybind11::dict geom{"type"_a="Point",
                            "coordinates"_a=pybind11::make_tuple(loc.lon(), loc.lat())};

        set_geoif(o.get_or_create_python_object(), o.get()->tags(), geom);
        return false;
    }

    bool filter_way(pyosmium::PyOSMWay &o) override
    {
        try {
            auto geom = json_loads(m_factory.create_linestring(*(o.get())));

            set_geoif(o.get_or_create_python_object(), o.get()->tags(), geom);
        } catch (const osmium::geometry_error& e) {
            return m_drop_invalid_geometries;
        }
        return false;
    }

    bool filter_relation(pyosmium::PyOSMRelation &o) override
    {
        return m_drop_invalid_geometries;
    }

    bool filter_area(pyosmium::PyOSMArea &o) override
    {
        try {
            auto geom = json_loads(m_factory.create_multipolygon(*(o.get())));

            set_geoif(o.get_or_create_python_object(), o.get()->tags(), geom);
        } catch (const osmium::geometry_error& e) {
            return false; //m_drop_invalid_geometries;
        }
        return false;
    }

private:
    void set_geoif(pybind11::object obj, osmium::TagList const &tags, pybind11::object &geom)
    {
        using namespace pybind11::literals;

        pybind11::dict props;
        if (m_tags.empty()) {
            for (auto const &tag: tags) {
                props[tag.key()] = tag.value();
            }
        } else {
            for (auto const &tag: tags) {
                if (std::find(m_tags.begin(), m_tags.end(), tag.key()) != m_tags.end()) {
                    props[tag.key()] = tag.value();
                }
            }
        }

        pybind11::dict gid("type"_a="Feature",
                           "properties"_a=props,
                           "geometry"_a=geom);

        pybind11::setattr(obj, "__geo_interface__", gid);
    }


    bool m_drop_invalid_geometries;
    std::vector<std::string> m_tags;
    osmium::geom::GeoJSONFactory<> m_factory;
    pybind11::object json_loads = pybind11::module_::import("json").attr("loads");
};

} // namespace

namespace pyosmium {

void init_geo_interface_filter(pybind11::module &m)
{
    pybind11::class_<GeoInterfaceFilter, pyosmium::BaseFilter, pyosmium::BaseHandler>(m, "GeoInterfaceFilter")
        .def(pybind11::init<bool, pybind11::iterable const &>(),
             pybind11::arg("drop_invalid_geometries") = true,
             pybind11::arg("tags") = pybind11::list())
    ;
}

} // namespace

