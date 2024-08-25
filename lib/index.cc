/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>
#include <osmium/index/map/all.hpp>
#include <osmium/index/node_locations_map.hpp>
#include <osmium/index/id_set.hpp>

namespace py = pybind11;

PYBIND11_MODULE(index, m)
{
    using LocationTable =
        osmium::index::map::Map<osmium::unsigned_object_id_type, osmium::Location>;
    using IndexFactory =
        osmium::index::MapFactory<osmium::unsigned_object_id_type, osmium::Location>;

    py::class_<LocationTable>(m, "LocationTable")
        .def("set", &LocationTable::set, py::arg("id"), py::arg("loc"))
        .def("get", &LocationTable::get, py::arg("id"))
        .def("used_memory", &LocationTable::used_memory)
        .def("clear", &LocationTable::clear)
        .def ("__setitem__", &LocationTable::set)
        .def ("__getitem__", &LocationTable::get)
    ;

    m.def("create_map", [](const std::string& config_string) {
            const auto& map_factory = IndexFactory::instance();
            return map_factory.create_map(config_string);
        },
        py::arg("map_type"));

    m.def("map_types", []() {
        const auto& map_factory = IndexFactory::instance();

        auto l = py::list();
        for (auto const &e : map_factory.map_types())
            l.append(e);

        return l;
        });

    using IdSet = osmium::index::IdSetDense<osmium::unsigned_object_id_type>;

    py::class_<IdSet>(m, "IdSet")
        .def(py::init<>())
        .def("set", &IdSet::set)
        .def("unset", &IdSet::unset)
        .def("get", &IdSet::get)
        .def("empty", &IdSet::empty)
        .def("clear", &IdSet::clear)
        .def("__len__", &IdSet::size)
        .def("__contains__", &IdSet::get)
    ;
}
