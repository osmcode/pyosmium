/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */

#include <pybind11/pybind11.h>

#include <osmium/area/assembler.hpp>
#include <osmium/area/multipolygon_manager.hpp>

#include "base_handler.h"
#include "handler_chain.h"

namespace py = pybind11;

namespace {

using MpManager = osmium::area::MultipolygonManager<osmium::area::Assembler>;

class AreaManagerSecondPassHandler : public BaseHandler
{
public:
    AreaManagerSecondPassHandler(MpManager *mp_manager, py::args args)
    : m_mp_manager(mp_manager), m_args(args), m_handlers(m_args)
    {
        m_mp_manager->set_callback([this](osmium::memory::Buffer &&ab)
                                          { osmium::apply(ab, this->m_handlers); });
    }

    void node(osmium::Node const *n) override
    {
        m_mp_manager->handle_node(*n);
    }

    void way(osmium::Way *w) override
    {
        m_mp_manager->handle_way(*w);
    }

    void relation(osmium::Relation const *r) override
    {
        m_mp_manager->handle_relation(*r);
    }

    void flush() override
    {
        m_mp_manager->flush_output();
    }

private:
    MpManager *m_mp_manager;
    py::args m_args;
    HandlerChain m_handlers;
};


class AreaManager : public BaseHandler
{
public:
    AreaManager()
    : m_mp_manager(m_assembler_config)
    {}

    BaseHandler *first_pass_handler() { return this; }

    // first-pass-handler
    void relation(osmium::Relation const *r) override
    {
        m_mp_manager.relation(*r);
    }

    AreaManagerSecondPassHandler *second_pass_handler(py::args args)
    {
        m_mp_manager.prepare_for_lookup();
        return new AreaManagerSecondPassHandler(&m_mp_manager, args);
    }

private:
    osmium::area::Assembler::config_type m_assembler_config;
    osmium::area::MultipolygonManager<osmium::area::Assembler> m_mp_manager;
};

}

PYBIND11_MODULE(_area, m)
{
    py::class_<AreaManagerSecondPassHandler, BaseHandler>(m,
                "AreaManagerSecondPassHandler");

    py::class_<AreaManager, BaseHandler>(m, "AreaManager",
        "Object manager class that manages building area objects from "
        "ways and relations.")
        .def(py::init<>())
        .def("first_pass_handler", &AreaManager::first_pass_handler,
             "Return the handler object used for the first pass of the "
             "file, which collects information about the relations.",
             py::return_value_policy::reference)
        .def("second_pass_handler", &AreaManager::second_pass_handler,
             "Return the handler object used for the second pass of the "
             "file, where areas are assembled. Pass the handlers that "
             "should handle the areas.",
             py::return_value_policy::take_ownership, py::keep_alive<1, 2>())
    ;
}
