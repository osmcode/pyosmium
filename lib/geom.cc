#include <boost/python.hpp>

#include <osmium/geom/haversine.hpp>

BOOST_PYTHON_MODULE(_geom)
{
    using namespace boost::python;
    def("haversine_distance", static_cast<double (*)(const osmium::WayNodeList&)>(&osmium::geom::haversine::distance));
}
