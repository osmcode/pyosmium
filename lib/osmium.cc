#include <boost/python.hpp>

#include <osmium/visitor.hpp>
#include <osmium/index/map/sparse_table.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>
#include <osmium/area/multipolygon_collector.hpp>
#include <osmium/area/assembler.hpp>

#include "generic_handler.hpp"

typedef osmium::index::map::SparseTable<osmium::unsigned_object_id_type, osmium::Location> sparse_index;
typedef osmium::handler::NodeLocationsForWays<sparse_index> location_handler_sparse;

void apply_reader_simple(osmium::io::Reader &rd, VirtualHandler &h) {
    osmium::apply(rd, h);
}

template <typename T>
void apply_reader_simple_with_location(osmium::io::Reader &rd,
                         osmium::handler::NodeLocationsForWays<T> &l,
                         VirtualHandler &h) {
    osmium::apply(rd, l, h);
}

void process_file_simple(const std::string &filename, VirtualHandler &h) {
    osmium::io::Reader reader(filename);

    osmium::apply(reader, h);
}



#include "osm.cc"
#include "index.cc"

BOOST_PYTHON_MODULE(_osmium)
{
    using namespace boost::python;

    enum_<SimpleHandlerWrap::location_index>("index_types")
        .value("SPARSE", SimpleHandlerWrap::sparse_index)
    ;

    enum_<SimpleHandlerWrap::pre_handler>("pre_handlers")
        .value("NONE", SimpleHandlerWrap::no_handler)
        .value("LOCATION", SimpleHandlerWrap::location_handler)
        .value("AREA", SimpleHandlerWrap::area_handler)
    ;

    class_<osmium::handler::NodeLocationsForWays<sparse_index>, boost::noncopyable>("SparseNodeLocationsForWays", 
            init<sparse_index&>())
    ;

    class_<SimpleHandlerWrap, boost::noncopyable>("SimpleHandler")
        .def("node", &VirtualHandler::node, &SimpleHandlerWrap::default_node)
        .def("way", &VirtualHandler::way, &SimpleHandlerWrap::default_way)
        .def("relation", &VirtualHandler::relation, &SimpleHandlerWrap::default_relation)
        .def("changeset", &VirtualHandler::changeset, &SimpleHandlerWrap::default_changeset)
        .def("area", &VirtualHandler::area, &SimpleHandlerWrap::default_area)
        .def("apply_file", &SimpleHandlerWrap::apply_file)
        .def("apply_file", &SimpleHandlerWrap::apply_file_no_index)
        .def("apply_file", &SimpleHandlerWrap::apply_file_no_handler)
    ;
    def("apply", &apply_reader_simple);
    def("apply", &apply_reader_simple_with_location<sparse_index>);
}
