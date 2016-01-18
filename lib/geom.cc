#include <boost/python.hpp>

#include <osmium/geom/haversine.hpp>
#include <osmium/geom/factory.hpp>
#include <osmium/geom/wkb.hpp>

class WKBFactory : public osmium::geom::WKBFactory<> {

public:
    WKBFactory()
    : osmium::geom::WKBFactory<>(osmium::geom::wkb_type::wkb, osmium::geom::out_type::hex)
    {}
};

BOOST_PYTHON_MODULE(geom)
{
    using namespace boost::python;
    docstring_options doc_options(true, true, false);

    enum_<osmium::geom::use_nodes>("use_nodes")
        .value("UNIQUE", osmium::geom::use_nodes::unique)
        .value("ALL", osmium::geom::use_nodes::all)
    ;

    enum_<osmium::geom::direction>("direction")
        .value("BACKWARD", osmium::geom::direction::backward)
        .value("FORWARD", osmium::geom::direction::forward)
    ;

    def("haversine_distance", static_cast<double (*)(const osmium::WayNodeList&)>(&osmium::geom::haversine::distance),
        arg("list"),
        "Compute the distance using the Haversine algorithm which takes the "
        "curvature of earth into account. If a :py:class:`WayNodeList` is given "
        "as a parameter the total length of the way in meters is computed.");

    class_<WKBFactory>("WKBFactory",
        "Factory that creates WKB from osmium geometries.")
        .add_property("epsg", &WKBFactory::epsg,
                      "(read-only) EPSG number of the output geometry.")
        .add_property("proj_string", &WKBFactory::proj_string,
                      "(read-only) projection string of the output geometry.")
        .def("create_point", static_cast<std::string (WKBFactory::*)(const osmium::Location&) const>(&WKBFactory::create_point),
             (arg("self"), arg("location")),
             "Create a point geometry from a :py:class:`osmium.osm.Location`.")
        .def("create_point", static_cast<std::string (WKBFactory::*)(const osmium::Node&)>(&WKBFactory::create_point),
             (arg("self"), arg("node")),
             "Create a point geometry from a :py:class:`osmium.osm.Node`.")
        .def("create_point", static_cast<std::string (WKBFactory::*)(const osmium::NodeRef&)>(&WKBFactory::create_point),
             (arg("self"), arg("ref")),
             "Create a point geometry from a :py:class:`osmium.osm.NodeRef`.")
        .def("create_linestring", static_cast<std::string (WKBFactory::*)(const osmium::WayNodeList&, osmium::geom::use_nodes, osmium::geom::direction)>(&WKBFactory::create_linestring),
             (arg("self"), arg("list"),
              arg("use_nodes")=osmium::geom::use_nodes::unique,
              arg("direction")=osmium::geom::direction::forward),
             "Create a LineString geometry from a :py:class:`osmium.osm.WayNodeList`.")
        .def("create_linestring", static_cast<std::string (WKBFactory::*)(const osmium::Way&, osmium::geom::use_nodes, osmium::geom::direction)>(&WKBFactory::create_linestring),
             (arg("self"), arg("way"),
              arg("use_nodes")=osmium::geom::use_nodes::unique,
              arg("direction")=osmium::geom::direction::forward),
             "Create a LineString geometry from a :py:class:`osmium.osm.Way`.")
        .def("create_multipolygon", &WKBFactory::create_multipolygon,
             (arg("self"), arg("area")),
             "Create a MultiPolygon geometry from a :py:class:`osmium.osm.Area`.")
    ;
}
