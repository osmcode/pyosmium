#include <pybind11/pybind11.h>

#include <osmium/geom/mercator_projection.hpp>
#include <osmium/geom/coordinates.hpp>
#include <osmium/geom/haversine.hpp>
#include <osmium/geom/factory.hpp>
#include <osmium/geom/wkb.hpp>
#include <osmium/geom/wkt.hpp>
#include <osmium/geom/geojson.hpp>

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
          (double (*)(const osmium::WayNodeList&)) &og::haversine::distance,
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

    py::class_<WKBFactory>(m, "WKBFactory",
        "Factory that creates WKB from osmium geometries.")
        .def(py::init<>())
        .def_property_readonly("epsg", &WKBFactory::epsg,
             "(read-only) EPSG number of the output geometry.")
        .def_property_readonly("proj_string", &WKBFactory::proj_string,
             "(read-only) projection string of the output geometry.")
        .def("create_point",
             (std::string (WKBFactory::*)(const osmium::Location&) const)
                 &WKBFactory::create_point,
             py::arg("location"),
             "Create a point geometry from a :py:class:`osmium.osm.Location`.")
        .def("create_point",
             (std::string (WKBFactory::*)(const osmium::Node&))
                 &WKBFactory::create_point,
             py::arg("node"),
             "Create a point geometry from a :py:class:`osmium.osm.Node`.")
        .def("create_point",
             (std::string (WKBFactory::*)(const osmium::NodeRef&))
               &WKBFactory::create_point,
             py::arg("ref"),
             "Create a point geometry from a :py:class:`osmium.osm.NodeRef`.")
        .def("create_linestring",
             (std::string (WKBFactory::*)(const osmium::WayNodeList&,
                                          og::use_nodes, og::direction))
                 &WKBFactory::create_linestring,
             py::arg("list"), py::arg("use_nodes")=og::use_nodes::unique,
             py::arg("direction")=og::direction::forward,
             "Create a LineString geometry from a :py:class:`osmium.osm.WayNodeList`.")
        .def("create_linestring",
             (std::string (WKBFactory::*)(const osmium::Way&, og::use_nodes,
                                          og::direction))
                 &WKBFactory::create_linestring,
             py::arg("way"), py::arg("use_nodes")=og::use_nodes::unique,
             py::arg("direction")=og::direction::forward,
             "Create a LineString geometry from a :py:class:`osmium.osm.Way`.")
        .def("create_multipolygon", &WKBFactory::create_multipolygon,
             py::arg("area"),
             "Create a MultiPolygon geometry from a :py:class:`osmium.osm.Area`.")
    ;

    py::class_<WKTFactory>(m, "WKTFactory",
        "Factory that creates WKT from osmium geometries.")
        .def(py::init<>())
        .def_property_readonly("epsg", &WKTFactory::epsg,
             "(read-only) EPSG number of the output geometry.")
        .def_property_readonly("proj_string", &WKTFactory::proj_string,
             "(read-only) projection string of the output geometry.")
        .def("create_point",
             (std::string (WKTFactory::*)(const osmium::Location&) const)
                 &WKTFactory::create_point,
             py::arg("location"),
             "Create a point geometry from a :py:class:`osmium.osm.Location`.")
        .def("create_point",
             (std::string (WKTFactory::*)(const osmium::Node&))
                 &WKTFactory::create_point,
             py::arg("node"),
             "Create a point geometry from a :py:class:`osmium.osm.Node`.")
        .def("create_point",
             (std::string (WKTFactory::*)(const osmium::NodeRef&))
                 &WKTFactory::create_point,
             py::arg("ref"),
             "Create a point geometry from a :py:class:`osmium.osm.NodeRef`.")
        .def("create_linestring",
             (std::string (WKTFactory::*)(const osmium::WayNodeList&,
                                          og::use_nodes, og::direction))
                  &WKTFactory::create_linestring,
             py::arg("list"), py::arg("use_nodes")=og::use_nodes::unique,
             py::arg("direction")=og::direction::forward,
             "Create a LineString geometry from a :py:class:`osmium.osm.WayNodeList`.")
        .def("create_linestring",
             (std::string (WKTFactory::*)(const osmium::Way&, og::use_nodes,
                                          og::direction))
                  &WKTFactory::create_linestring,
             py::arg("way"), py::arg("use_nodes")=og::use_nodes::unique,
             py::arg("direction")=og::direction::forward,
             "Create a LineString geometry from a :py:class:`osmium.osm.Way`.")
        .def("create_multipolygon", &WKTFactory::create_multipolygon,
             py::arg("area"),
             "Create a MultiPolygon geometry from a :py:class:`osmium.osm.Area`.")
    ;

    py::class_<GeoJSONFactory>(m, "GeoJSONFactory",
        "Factory that creates GeoJSON geometries from osmium geometries.")
        .def(py::init<>())
        .def_property_readonly("epsg", &GeoJSONFactory::epsg,
             "(read-only) EPSG number of the output geometry.")
        .def_property_readonly("proj_string", &GeoJSONFactory::proj_string,
             "(read-only) projection string of the output geometry.")
        .def("create_point",
             (std::string (GeoJSONFactory::*)(const osmium::Location&) const)
                 &GeoJSONFactory::create_point,
             py::arg("location"),
             "Create a point geometry from a :py:class:`osmium.osm.Location`.")
        .def("create_point",
             (std::string (GeoJSONFactory::*)(const osmium::Node&))
                 &GeoJSONFactory::create_point,
             py::arg("node"),
             "Create a point geometry from a :py:class:`osmium.osm.Node`.")
        .def("create_point",
             (std::string (GeoJSONFactory::*)(const osmium::NodeRef&))
                 &GeoJSONFactory::create_point,
             py::arg("ref"),
             "Create a point geometry from a :py:class:`osmium.osm.NodeRef`.")
        .def("create_linestring",
             (std::string (GeoJSONFactory::*)(const osmium::WayNodeList&,
                                              og::use_nodes, og::direction))
                 &GeoJSONFactory::create_linestring,
             py::arg("list"), py::arg("use_nodes")=og::use_nodes::unique,
             py::arg("direction")=og::direction::forward,
             "Create a LineString geometry from a :py:class:`osmium.osm.WayNodeList`.")
        .def("create_linestring",
             (std::string (GeoJSONFactory::*)(const osmium::Way&, og::use_nodes,
                                              og::direction))
                 &GeoJSONFactory::create_linestring,
             py::arg("way"), py::arg("use_nodes")=og::use_nodes::unique,
             py::arg("direction")=og::direction::forward,
             "Create a LineString geometry from a :py:class:`osmium.osm.Way`.")
        .def("create_multipolygon", &GeoJSONFactory::create_multipolygon,
             py::arg("area"),
             "Create a MultiPolygon geometry from a :py:class:`osmium.osm.Area`.")
    ;
}
