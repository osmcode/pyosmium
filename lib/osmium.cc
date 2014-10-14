#include <boost/python.hpp>

#include <osmium/visitor.hpp>
#include <osmium/index/map/sparse_table.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>
#include <osmium/area/multipolygon_collector.hpp>
#include <osmium/area/assembler.hpp>

#include "generic_handler.hpp"

template <typename T>
void apply_reader_simple(osmium::io::Reader &rd, T &h) {
    osmium::apply(rd, h);
}


template <typename T>
void apply_reader_simple_with_location(osmium::io::Reader &rd,
                         osmium::handler::NodeLocationsForWays<T> &l,
                         VirtualHandler &h) {
    osmium::apply(rd, l, h);
}

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

    class_<osmium::handler::NodeLocationsForWays<SparseLocationTable>, boost::noncopyable>("NodeLocationsForWays", 
            init<SparseLocationTable&>())
    ;
    class_<osmium::handler::NodeLocationsForWays<DenseLocationMapFile>, boost::noncopyable>("NodeLocationsForWays", 
            init<DenseLocationMapFile&>())
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
    def("apply", &apply_reader_simple<VirtualHandler>);
    def("apply", &apply_reader_simple<osmium::handler::NodeLocationsForWays<DenseLocationMapFile>>);
    def("apply", &apply_reader_simple_with_location<SparseLocationTable>);
    def("apply", &apply_reader_simple_with_location<DenseLocationMapFile>);
}
