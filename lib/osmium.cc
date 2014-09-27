#include <boost/python.hpp>

#include <osmium/visitor.hpp>

#include "generic_handler.hpp"

void apply_reader_simple(osmium::io::Reader &rd, VirtualHandler &h) {
    osmium::apply(rd, h);
}


#include "osm.cc"

BOOST_PYTHON_MODULE(_osmium)
{
    using namespace boost::python;
    
    class_<SimpleHandlerWrap, boost::noncopyable>("SimpleHandler")
        .def("node", &VirtualHandler::node, &SimpleHandlerWrap::default_node)
        .def("way", &VirtualHandler::way, &SimpleHandlerWrap::default_way)
        .def("relation", &VirtualHandler::relation, &SimpleHandlerWrap::default_relation)
        .def("changeset", &VirtualHandler::changeset, &SimpleHandlerWrap::default_changeset)
    ;
    def("apply", &apply_reader_simple);
}
