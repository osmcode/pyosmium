#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>
#include <osmium/osm/entity_bits.hpp>
#include <osmium/index/map/all.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>

#include "simple_handler.h"
#include "osmium_module.h"

namespace py = pybind11;

PYBIND11_MODULE(_osmium, m) {
    using LocationTable =
        osmium::index::map::Map<osmium::unsigned_object_id_type, osmium::Location>;
    using NodeLocationHandler =
        osmium::handler::NodeLocationsForWays<LocationTable>;

    py::register_exception<osmium::invalid_location>(m, "InvalidLocationError");
    py::register_exception_translator([](std::exception_ptr p) {
        try {
            if (p) std::rethrow_exception(p);
        } catch (const osmium::not_found &e) {
            PyErr_SetString(PyExc_KeyError, e.what());
        }
    });

    py::class_<osmium::handler::NodeLocationsForWays<LocationTable>>(
        m, "NodeLocationsForWays")
        .def(py::init<LocationTable&>())
        .def("ignore_errors", &osmium::handler::NodeLocationsForWays<LocationTable>::ignore_errors)
    ;

    m.def("apply", [](osmium::io::Reader &rd, BaseHandler &h)
                   { py::gil_scoped_release release; osmium::apply(rd, h); },
          py::arg("reader"), py::arg("handler"),
          "Apply a chain of handlers.");
    m.def("apply", [](osmium::io::Reader &rd, NodeLocationHandler &h)
                   { py::gil_scoped_release release; osmium::apply(rd, h); },
          py::arg("reader"), py::arg("handler"),
          "Apply a chain of handlers.");
    m.def("apply", [](osmium::io::Reader &rd, NodeLocationHandler &l,
                      BaseHandler &h)
                     { py::gil_scoped_release release; osmium::apply(rd, l, h); },
          py::arg("reader"), py::arg("node_handler"), py::arg("handler"),
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
             py::arg("idx")="flex_mem",
             "Apply the handler to the given file. If locations is true, then\n"
             "a location handler will be applied before, which saves the node\n"
             "positions. In that case, the type of this position index can be\n"
             "further selected in idx. If an area callback is implemented, then\n"
             "the file will be scanned twice and a location handler and a\n"
             "handler for assembling multipolygons and areas from ways will\n"
             "be executed.")
        .def("apply_buffer", &SimpleHandler::apply_buffer,
             py::arg("buffer"), py::arg("format"),
             py::arg("locations")=false, py::arg("idx")="flex_mem",
             "Apply the handler to a string buffer. The buffer must be a\n"
             "byte string.")
        ;

    init_merge_input_reader(m);
    init_write_handler(m);
    init_simple_writer(m);
};
