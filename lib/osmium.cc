#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>
#include <osmium/osm/entity_bits.hpp>
#include <osmium/index/map/all.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>

#include "simple_handler.h"
#include "simple_writer.h"
#include "write_handler.h"

namespace py = pybind11;

PYBIND11_MODULE(_osmium, m) {
    using LocationTable =
        osmium::index::map::Map<osmium::unsigned_object_id_type, osmium::Location>;
    using NodeLocationHandler =
        osmium::handler::NodeLocationsForWays<LocationTable>;

    py::register_exception<osmium::invalid_location>(m, "InvalidLocationError");
    py::register_exception<osmium::not_found>(m, "OsmiumKeyError");

    m.def("apply", [](osmium::io::Reader &rd, BaseHandler &h)
                   { osmium::apply(rd, h); },
        "Apply a chain of handlers.");
    m.def("apply", [](osmium::io::Reader &rd, NodeLocationHandler &h)
                   { osmium::apply(rd, h); },
        "Apply a chain of handlers.");
    m.def("apply", [](osmium::io::Reader &rd, NodeLocationHandler &l,
                      BaseHandler &h)
                     { osmium::apply(rd, l, h); },
        "Apply a chain of handlers.");

    py::class_<BaseHandler>(m, "BaseHandler");

    py::class_<SimpleHandler, PySimpleHandler, BaseHandler>(m, "SimpleHandler",
        "The most generic of OSM data handlers. Derive your data processor "
        "from this class and implement callbacks for each object type you are "
        "interested in. The following data types are recognised: \n"
        " `node`, `way`, `relation`, `area` and `changeset`.\n "
        "A callback takes exactly one parameter which is the object. Note that "
        "all objects that are handed into the handler are only readable and are "
        "only valid until the end of the callback is reached. Any data that "
        "should be retained must be copied into other data structures.")
        .def(py::init<>())
        .def("apply_file", &SimpleHandler::apply_file,
             py::arg("filename"), py::arg("locations")=false,
             py::arg("idx")="sparse_mem_array",
             "Apply the handler to the given file. If locations is true, then\n"
             "a location handler will be applied before, which saves the node\n"
             "positions. In that case, the type of this position index can be\n"
             "further selected in idx. If an area callback is implemented, then\n"
             "the file will be scanned twice and a location handler and a\n"
             "handler for assembling multipolygons and areas from ways will\n"
             "be executed.");

    py::class_<WriteHandler, BaseHandler>(m, "WriteHandler",
        "Handler function that writes all data directly to a file."
        "The handler takes a file name as its mandatory parameter. The file "
        "must not yet exist. The file type to output is determined from the "
        "file extension. "
        "The second (optional) parameter is the buffer size. osmium caches the "
        "output data in an internal memory buffer before writing it on disk. This "
        "parameter allows changing the default buffer size of 4MB. Larger buffers "
        "are normally better but you should be aware that there are normally multiple "
        "buffers in use during the write process.")
        .def(py::init<const char*, unsigned long>())
        .def(py::init<const char*>())
        .def("close", &WriteHandler::close,
             "Flush the remaining buffers and close the writer. While it is not "
             "strictly necessary to call this function explicitly, it is still "
             "strongly recommended to close the writer as soon as possible, so "
             "that the buffer memory can be freed.")
    ;

    py::class_<SimpleWriter>(m, "SimpleWriter",
        "The most generic class to write osmium objects into a file. The writer "
        "takes a file name as its mandatory parameter. The file must not yet "
        "exist. The file type to output is determined from the file extension. "
        "The second (optional) parameter is the buffer size. osmium caches the "
        "output data in an internal memory buffer before writing it on disk. This "
        "parameter allows changing the default buffer size of 4MB. Larger buffers "
        "are normally better but you should be aware that there are normally multiple "
        "buffers in use during the write process.")
        .def(py::init<const char*, unsigned long>())
        .def(py::init<const char*>())
        .def("add_node", &SimpleWriter::add_node, py::arg("node"),
             "Add a new node to the file. The node may be an ``osmium.osm.Node`` object, "
             "an ``osmium.osm.mutable.Node`` object or any other Python object that "
             "implements the same attributes.")
        .def("add_way", &SimpleWriter::add_way, py::arg("way"),
             "Add a new way to the file. The way may be an ``osmium.osm.Way`` object, "
             "an ``osmium.osm.mutable.Way`` object or any other Python object that "
             "implements the same attributes.")
        .def("add_relation", &SimpleWriter::add_relation, py::arg("relation"),
             "Add a new relation to the file. The relation may be an "
             "``osmium.osm.Relation`` object, an ``osmium.osm.mutable.Way`` "
             "object or any other Python object that implements the same attributes.")
        .def("close", &SimpleWriter::close,
             "Flush the remaining buffers and close the writer. While it is not "
             "strictly necessary to call this function explicitly, it is still "
             "strongly recommended to close the writer as soon as possible, so "
             "that the buffer memory can be freed.")
    ;
};
