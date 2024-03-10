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
#include <osmium/index/index.hpp>
#include <osmium/visitor.hpp>

#include "base_handler.h"
#include "osmium_module.h"
#include "python_handler.h"
#include "handler_chain.h"

namespace py = pybind11;

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
                         HandlerChain handler{args};
                         {
                             py::gil_scoped_release release;
                             osmium::apply(rd, handler);
                         }
                     },
          py::arg("reader"),
          "Apply a chain of handlers.");

    py::class_<BaseHandler>(m, "BaseHandler");

    init_merge_input_reader(m);
    init_write_handler(m);
    init_simple_writer(m);
    init_node_location_handler(m);
};
