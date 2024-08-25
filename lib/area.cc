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
#include "buffer_iterator.h"

namespace py = pybind11;

namespace {

using MpManager = osmium::area::MultipolygonManager<osmium::area::Assembler>;

class AreaManagerSecondPassHandlerBase : public pyosmium::BaseHandler
{
public:
    AreaManagerSecondPassHandlerBase(MpManager *mp_manager)
    : m_mp_manager(mp_manager)
    {
        m_enabled_for = osmium::osm_entity_bits::nwr;
    }


    bool node(pyosmium::PyOSMNode &n) override
    {
        m_mp_manager->handle_node(*(n.get()));
        return false;
    }

    bool way(pyosmium::PyOSMWay &w) override
    {
        m_mp_manager->handle_way(*(w.get()));
        return false;
    }

    bool relation(pyosmium::PyOSMRelation &r) override
    {
        m_mp_manager->handle_relation(*(r.get()));
        return false;
    }

    void flush() override
    {
        m_mp_manager->flush_output();
    }

protected:
    MpManager *m_mp_manager;
};


class AreaManagerSecondPassHandler : public AreaManagerSecondPassHandlerBase
{
public:
    AreaManagerSecondPassHandler(MpManager *mp_manager, py::args args)
    : AreaManagerSecondPassHandlerBase(mp_manager), m_args(args), m_handlers(m_args)
    {
        m_mp_manager->set_callback([this](osmium::memory::Buffer &&buffer) {
        for (auto &obj : buffer.select<osmium::Area>()) {
                pyosmium::PyOSMArea area{&obj};
                this->m_handlers.area(area);
            }
        });
    }

private:
    py::args m_args;
    pyosmium::HandlerChain m_handlers;

};


class AreaManagerBufferHandler : public AreaManagerSecondPassHandlerBase
{
public:
    AreaManagerBufferHandler(MpManager *mp_manager, pyosmium::BufferIterator *cb)
    : AreaManagerSecondPassHandlerBase(mp_manager)
    {
        m_mp_manager->set_callback([cb](osmium::memory::Buffer &&ab)
                                       { cb->add_buffer(std::move(ab)); });
    }
};


class AreaManager : public pyosmium::BaseHandler
{
public:
    AreaManager()
    : m_mp_manager(m_assembler_config)
    {}

    pyosmium::BaseHandler *first_pass_handler() { return this; }

    // first-pass-handler
    bool relation(pyosmium::PyOSMRelation &r) override
    {
        m_mp_manager.relation(*(r.get()));
        return false;
    }

    AreaManagerSecondPassHandler *second_pass_handler(py::args args)
    {
        m_mp_manager.prepare_for_lookup();
        return new AreaManagerSecondPassHandler(&m_mp_manager, args);
    }

    AreaManagerBufferHandler *second_pass_to_buffer(pyosmium::BufferIterator *cb)
    {
        m_mp_manager.prepare_for_lookup();
        return new AreaManagerBufferHandler(&m_mp_manager, cb);
    }

private:
    osmium::area::Assembler::config_type m_assembler_config;
    osmium::area::MultipolygonManager<osmium::area::Assembler> m_mp_manager;
};

} // namespace

PYBIND11_MODULE(area, m)
{
    py::class_<AreaManagerSecondPassHandler, pyosmium::BaseHandler>(m,
                "AreaManagerSecondPassHandler");
    py::class_<AreaManagerBufferHandler, pyosmium::BaseHandler>(m,
                "AreaManagerBufferHandler");

    py::class_<AreaManager, pyosmium::BaseHandler>(m, "AreaManager")
        .def(py::init<>())
        .def("first_pass_handler", &AreaManager::first_pass_handler,
             py::return_value_policy::reference)
        .def("second_pass_handler", &AreaManager::second_pass_handler,
             py::return_value_policy::take_ownership, py::keep_alive<1, 2>())
        .def("second_pass_to_buffer", &AreaManager::second_pass_to_buffer,
             py::keep_alive<1, 2>())
    ;
}
