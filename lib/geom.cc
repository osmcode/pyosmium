#include <boost/python.hpp>

#include <osmium/geom/haversine.hpp>
#include <osmium/geom/factory.hpp>
#include <osmium/geom/wkb.hpp>

BOOST_PYTHON_MODULE(_geom)
{
    using namespace boost::python;
    def("haversine_distance", static_cast<double (*)(const osmium::WayNodeList&)>(&osmium::geom::haversine::distance));

    using WKBFactory = osmium::geom::WKBFactory<>;
    class_<WKBFactory>("WKBFactory")
        .add_property("epsg", &WKBFactory::epsg)
        .add_property("proj_string", &WKBFactory::proj_string)
        .def("create_point", static_cast<std::string (WKBFactory::*)(const osmium::Location) const>(&WKBFactory::create_point))
        .def("create_point", static_cast<std::string (WKBFactory::*)(const osmium::Node&)>(&WKBFactory::create_point))
        .def("create_point", static_cast<std::string (WKBFactory::*)(const osmium::NodeRef&)>(&WKBFactory::create_point))
        .def("create_linestring", static_cast<std::string (WKBFactory::*)(const osmium::WayNodeList&, osmium::geom::use_nodes, osmium::geom::direction)>(&WKBFactory::create_linestring))
        .def("create_linestring", static_cast<std::string (WKBFactory::*)(const osmium::Way&, osmium::geom::use_nodes, osmium::geom::direction)>(&WKBFactory::create_linestring))
        .def("create_multipolygon", &WKBFactory::create_multipolygon)
    ;
}
