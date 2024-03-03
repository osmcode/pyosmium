/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <vector>

#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>
#include <osmium/handler.hpp>

#include "simple_handler.h"
#include "osmium_module.h"

namespace py = pybind11;

class HandlerChain : public osmium::handler::Handler
{
public:
    HandlerChain(std::vector<BaseHandler *> &&handlers)
    : m_handlers(handlers)
    {}

    void node(osmium::Node const &o) {
        for (auto const &handler : m_handlers) {
            handler->node(&o);
        }
    }

    void way(osmium::Way &w) {
        for (auto const &handler : m_handlers) {
            handler->way(&w);
        }
    }

    void relation(osmium::Relation const &o) {
        for (auto const &handler : m_handlers) {
            handler->relation(&o);
        }
    }

    void changeset(osmium::Changeset const &o) {
        for (auto const &handler : m_handlers) {
            handler->changeset(&o);
        }
    }

    void area(osmium::Area const &o) {
        for (auto const &handler : m_handlers) {
            handler->area(&o);
        }
    }

private:
    std::vector<BaseHandler *> m_handlers;
};


static HandlerChain make_handler_chain(py::args args)
{
    std::vector<BaseHandler *> handlers;
    for (auto const &arg: args) {
        if (py::isinstance<BaseHandler>(arg)) {
            handlers.push_back(arg.cast<BaseHandler *>());
        } else {
            throw py::type_error{"Argument must be a handler-like object."};
        }
    }

    return HandlerChain(std::move(handlers));
}

PYBIND11_MODULE(_osmium, m) {
    py::register_exception<osmium::invalid_location>(m, "InvalidLocationError");
    py::register_exception_translator([](std::exception_ptr p) {
        try {
            if (p) std::rethrow_exception(p);
        } catch (const osmium::not_found &e) {
            PyErr_SetString(PyExc_KeyError, e.what());
        }
    });

    m.def("apply", [](osmium::io::Reader &rd, BaseHandler &h)
                   { py::gil_scoped_release release; osmium::apply(rd, h); },
          py::arg("reader"), py::arg("handler"),
          "Apply a single handler.");
    m.def("apply", [](osmium::io::Reader &rd, py::args args)
                     {
                         auto handler = make_handler_chain(args);
                         {
                             py::gil_scoped_release release;
                             osmium::apply(rd, handler);
                         }
                     },
          py::arg("reader"),
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
    init_node_location_handler(m);
};
