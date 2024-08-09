/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#ifndef PYOSMIUM_BUFFER_ITERATOR_H
#define PYOSMIUM_BUFFER_ITERATOR_H
#include <queue>

#include <pybind11/pybind11.h>

#include "osmium_module.h"
#include "osm_base_objects.h"
#include "handler_chain.h"

namespace pyosmium {

class BufferIterator
{
public:
    BufferIterator(pybind11::args args)
    : m_handler(args)
    {}

    void add_buffer(osmium::memory::Buffer &&buf)
    {
        if (m_buffers.empty()) {
            m_current_it = buf.begin();
        }

        m_buffers.push(std::move(buf));
    }

    bool empty() const
    { return m_buffers.empty(); }

    pybind11::object next()
    {
        m_current.emplace<bool>(false);

        if (m_buffers.empty()) {
            throw pybind11::stop_iteration();
        }

        while (true) {
            while (m_current_it == m_buffers.front().end()) {
                m_buffers.pop();
                if (m_buffers.empty()) {
                    throw pybind11::stop_iteration();
                }
                m_current_it = m_buffers.front().begin();
            }

            osmium::OSMEntity *entity = &*m_current_it;
            ++m_current_it;

            switch (entity->type()) {
                case osmium::item_type::node:
                {
                    auto &obj = m_current.emplace<PyOSMNode>(entity);
                    if (!m_handler.node(obj)) {
                        return obj.get_or_create_python_object();
                    }
                    break;
                }
                case osmium::item_type::way:
                {
                    auto &obj = m_current.emplace<PyOSMWay>(entity);
                    if (!m_handler.way(obj)) {
                        return obj.get_or_create_python_object();
                    }
                    break;
                }
                case osmium::item_type::relation:
                {
                    auto &obj = m_current.emplace<PyOSMRelation>(entity);
                    if (!m_handler.relation(obj)) {
                        return obj.get_or_create_python_object();
                    }
                    break;
                }
                case osmium::item_type::area:
                {
                    auto &obj = m_current.emplace<PyOSMArea>(entity);
                    if (!m_handler.area(obj)) {
                        return obj.get_or_create_python_object();
                    }
                    break;
                }
                case osmium::item_type::changeset:
                {
                    auto &obj = m_current.emplace<PyOSMChangeset>(entity);
                    if (!m_handler.changeset(obj)) {
                        return obj.get_or_create_python_object();
                    }
                    break;
                }
                default:
                    break;
            }
        }

        return pybind11::object();
    }


private:
    HandlerChain m_handler;

    std::queue<osmium::memory::Buffer> m_buffers;
    osmium::memory::Buffer::iterator m_current_it;
    PyOSMAny m_current = false;
};

} // namespace

#endif // PYOSMIUM_BUFFER_ITERATOR_H
