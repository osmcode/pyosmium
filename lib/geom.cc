/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2023 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <osmium/geom/mercator_projection.hpp>
#include <osmium/geom/coordinates.hpp>
#include <osmium/geom/haversine.hpp>
#include <osmium/geom/factory.hpp>
#include <osmium/geom/wkb.hpp>
#include <osmium/geom/wkt.hpp>
#include <osmium/geom/geojson.hpp>

#include "cast.h"
#include "osm_base_objects.h"

namespace py = pybind11;
namespace og = osmium::geom;

struct WKBFactory : osmium::geom::WKBFactory<>
{
public:
    WKBFactory()
    : og::WKBFactory<>(og::wkb_type::wkb, og::out_type::hex)
    {}
};

using WKTFactory = og::WKTFactory<>;
using GeoJSONFactory = og::GeoJSONFactory<>;

template <typename Factory>
void make_factory_class(py::module_ &m, char const *name, char const *doc)
{
    py::class_<Factory>(m, name, doc)
        .def(py::init<>())
        .def_property_readonly("epsg", &Factory::epsg,
             "(read-only) EPSG number of the output geometry.")
        .def_property_readonly("proj_string", &Factory::proj_string,
             "(read-only) projection string of the output geometry.")
        .def("create_point",
             [](Factory &f, py::object const &o) {
                 if (py::isinstance<osmium::Location>(o)) {
                    return f.create_point(o.cast<osmium::Location const &>());
                 }
                 auto const *node = pyosmium::try_cast<COSMNode>(o);
                 if (node) {
                    return f.create_point(*node->get());
                 }

                 return f.create_point(o.attr("location").cast<osmium::Location const &>());
             },
             py::arg("pt"),
             "Create a point geometry from a :py:class:`osmium.osm.Node`.")
        .def("create_linestring",
             [](Factory &f, py::object const &o, og::use_nodes un, og::direction dir) {
                 auto const *way = pyosmium::try_cast<COSMWay>(o);
                 if (way) {
                    return f.create_linestring(*way->get(), un, dir);
                 }

                 return f.create_linestring(pyosmium::cast_list<osmium::WayNodeList>(o), un, dir);
             },
             py::arg("list"), py::arg("use_nodes")=og::use_nodes::unique,
             py::arg("direction")=og::direction::forward,
             "Create a LineString geometry from a :py:class:`osmium.osm.Way`.")
        .def("create_multipolygon",
             [](Factory &f, py::object const &o) {
                 return f.create_multipolygon(*pyosmium::cast<COSMArea>(o).get());
             },
             py::arg("area"),
             "Create a MultiPolygon geometry from a :py:class:`osmium.osm.Area`.")
    ;
}

PYBIND11_MODULE(geom, m)
{
    py::enum_<og::use_nodes>(m, "use_nodes")
        .value("UNIQUE", og::use_nodes::unique)
        .value("ALL", og::use_nodes::all)
        .export_values()
    ;

    py::enum_<og::direction>(m, "direction")
        .value("BACKWARD", og::direction::backward)
        .value("FORWARD", og::direction::forward)
        .export_values()
    ;

    py::class_<osmium::geom::Coordinates>(m, "Coordinates",
        "Class representing coordinates")
        .def(py::init<>())
        .def(py::init<double, double>())
        .def(py::init<osmium::Location const &>())
        .def_readonly("x", &osmium::geom::Coordinates::x,
            "(read-only) X coordinate.")
        .def_readonly("y", &osmium::geom::Coordinates::y,
            "(read-only) Y coordinate.")
        .def("valid", &osmium::geom::Coordinates::valid,
            "True if coordinates are valid")
    ;

    m.def("haversine_distance",
          [](py::object const &o) { return og::haversine::distance(pyosmium::cast_list<osmium::WayNodeList>(o)); },
          py::arg("list"),
        "Compute the distance using the Haversine algorithm which takes the "
        "curvature of earth into account. If a :py:class:`WayNodeList` is given "
        "as a parameter the total length of the way in meters is computed.");

    m.def("lonlat_to_mercator", &og::lonlat_to_mercator,
          py::arg("coordinate"),
        "Convert coordinates from WGS84 to Mercator projection.");

    m.def("mercator_to_lonlat", &og::mercator_to_lonlat,
          py::arg("coordinate"),
        "Convert coordinates from WGS84 to Mercator projection.");

    make_factory_class<WKBFactory>(m, "WKBFactory",
        "Factory that creates WKB from osmium geometries.");

    make_factory_class<WKTFactory>(m, "WKTFactory",
        "Factory that creates WKT from osmium geometries.");

    make_factory_class<GeoJSONFactory>(m, "GeoJSONFactory",
        "Factory that creates GeoJSON geometries from osmium geometries.");
}
