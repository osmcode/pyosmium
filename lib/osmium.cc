/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>
#include <pybind11/stl/filesystem.h>

#include <osmium/osm.hpp>
#include <osmium/handler.hpp>
#include <osmium/index/index.hpp>
#include <osmium/visitor.hpp>

#include "osm_base_objects.h"
#include "base_handler.h"
#include "base_filter.h"
#include "osmium_module.h"
#include "python_handler.h"
#include "handler_chain.h"
#include "buffer_iterator.h"

#include <vector>
#include <filesystem>

namespace py = pybind11;

void pyosmium::apply_item(osmium::OSMEntity &obj, pyosmium::BaseHandler &handler)
{
    switch (obj.type()) {
        case osmium::item_type::node:
        {
            PyOSMNode node{static_cast<osmium::Node *>(&obj)};
            handler.node(node);
            break;
        }
        case osmium::item_type::way:
        {
            PyOSMWay way{static_cast<osmium::Way *>(&obj)};
            handler.way(way);
            break;
        }
        case osmium::item_type::relation:
        {
            PyOSMRelation rel{static_cast<osmium::Relation *>(&obj)};
            handler.relation(rel);
            break;
        }
        case osmium::item_type::area:
        {
            PyOSMArea area{static_cast<osmium::Area *>(&obj)};
            handler.area(area);
            break;
        }
        case osmium::item_type::changeset:
        {
            PyOSMChangeset chg{static_cast<osmium::Changeset *>(&obj)};
            handler.changeset(chg);
            break;
        }
    }
}

void pyosmium::apply(osmium::io::Reader &reader, pyosmium::BaseHandler &handler)
{
    while (auto buffer = reader.read()) {
        for (auto &obj : buffer.select<osmium::OSMEntity>()) {
            pyosmium::apply_item(obj, handler);
        }
    }
    handler.flush();
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

    m.def("apply", &pyosmium::apply,
          py::arg("reader"), py::arg("handler"));
    m.def("apply", [](osmium::io::Reader &rd, py::args args)
                     {
                         pyosmium::HandlerChain handler{args};
                         pyosmium::apply(rd, handler);
                     },
          py::arg("reader"));
    m.def("apply", [](std::string fn, pyosmium::BaseHandler &h)
                   {
                       osmium::io::Reader rd{fn};
                       pyosmium::apply(rd, h);
                   },
          py::arg("filename"), py::arg("handler"));
    m.def("apply", [](std::string fn, py::args args)
                     {
                         pyosmium::HandlerChain handler{args};
                         osmium::io::Reader rd{fn};
                         pyosmium::apply(rd, handler);
                     },
          py::arg("filename"));
    m.def("apply", [](std::filesystem::path const &fn, pyosmium::BaseHandler &h)
                   {
                       osmium::io::Reader rd{fn.string()};
                       pyosmium::apply(rd, h);
                   },
          py::arg("filename"), py::arg("handler"));
    m.def("apply", [](std::filesystem::path const &fn, py::args args)
                     {
                         pyosmium::HandlerChain handler{args};
                         osmium::io::Reader rd{fn.string()};
                         pyosmium::apply(rd, handler);
                     },
          py::arg("filename"));
    m.def("apply", [](osmium::io::File fn, pyosmium::BaseHandler &h)
                   {
                       osmium::io::Reader rd{fn};
                       pyosmium::apply(rd, h);
                   },
          py::arg("filename"), py::arg("handler"));
    m.def("apply", [](osmium::io::File fn, py::args args)
                     {
                         pyosmium::HandlerChain handler{args};
                         osmium::io::Reader rd{fn};
                         pyosmium::apply(rd, handler);
                     },
          py::arg("filename"));

    py::class_<pyosmium::BaseHandler>(m, "BaseHandler");
    py::class_<pyosmium::BaseFilter, pyosmium::BaseHandler>(m, "BaseFilter")
        .def("enable_for", &pyosmium::BaseFilter::enable_for,
             py::arg("entities"))
    ;

    py::class_<pyosmium::BufferIterator>(m, "BufferIterator")
    .def(py::init<py::args>())
    .def("__bool__", [](pyosmium::BufferIterator const &it) { return !it.empty(); })
    .def("__iter__", [](py::object const &self) { return self; })
    .def("__next__", &pyosmium::BufferIterator::next)
    ;

    pyosmium::init_merge_input_reader(m);
    pyosmium::init_simple_writer(m);
    pyosmium::init_node_location_handler(m);
    pyosmium::init_osm_file_iterator(m);
    pyosmium::init_id_tracker(m);
};
