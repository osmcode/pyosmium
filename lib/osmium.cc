#include <boost/python.hpp>

#include <osmium/visitor.hpp>
#include <osmium/index/map/sparse_table.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>

#include "generic_handler.hpp"

typedef osmium::index::map::SparseTable<osmium::unsigned_object_id_type, osmium::Location> sparse_index;

void apply_reader_simple(osmium::io::Reader &rd, VirtualHandler &h) {
    osmium::apply(rd, h);
}

void apply_reader_simple_with_location(osmium::io::Reader &rd,
                         osmium::handler::NodeLocationsForWays<sparse_index> &l,
                         VirtualHandler &h) {
    osmium::apply(rd, l, h);
}



#include "osm.cc"
#include "index.cc"

BOOST_PYTHON_MODULE(_osmium)
{
    using namespace boost::python;

    class_<osmium::handler::NodeLocationsForWays<sparse_index>, boost::noncopyable>("SparseNodeLocationsForWays", 
            init<sparse_index&>())
    ;

    class_<SimpleHandlerWrap, boost::noncopyable>("SimpleHandler")
        .def("node", &VirtualHandler::node, &SimpleHandlerWrap::default_node)
        .def("way", &VirtualHandler::way, &SimpleHandlerWrap::default_way)
        .def("relation", &VirtualHandler::relation, &SimpleHandlerWrap::default_relation)
        .def("changeset", &VirtualHandler::changeset, &SimpleHandlerWrap::default_changeset)
    ;
    def("apply", &apply_reader_simple);
    def("apply", &apply_reader_simple_with_location);
}
