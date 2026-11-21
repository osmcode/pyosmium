/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2026 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include "base_filter.h"
#include "handler_chain.h"

namespace {

class InvertFilter : public pyosmium::BaseFilter
{
public:
    InvertFilter(pybind11::args args)
    : m_handler(args)
    {}

    bool filter_node(pyosmium::PyOSMNode &o) override
    {
        return !m_handler.node(o);
    }

    bool filter_way(pyosmium::PyOSMWay &o) override
    {
        return !m_handler.way(o);
    }

    bool filter_relation(pyosmium::PyOSMRelation &o) override
    {
        return !m_handler.relation(o);
    }

    bool filter_area(pyosmium::PyOSMArea &o) override
    {
        return !m_handler.area(o);
    }

    bool filter_changeset(pyosmium::PyOSMChangeset &o) override
    {
        return !m_handler.changeset(o);
    }

private:
    pyosmium::HandlerChain m_handler;
};

} // namespace

namespace pyosmium {

void init_invert_filter(pybind11::module &m)
{
    pybind11::class_<InvertFilter, pyosmium::BaseFilter, pyosmium::BaseHandler>(m, "InvertFilter")
        .def(py::init<pybind11::args>())
    ;
}

} // namespace
