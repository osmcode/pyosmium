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

    ~BufferIterator()
    {
        invalidate_current();
    }

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
        invalidate_current();

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
                    auto *node = static_cast<osmium::Node *>(entity);
                    if (!m_handler.handle_node(*node)) {
                        m_current = m_type_module.attr("Node")(COSMNode{node});
                        m_current_type = osmium::item_type::node;
                        return m_current;
                    }
                    break;
                }
                case osmium::item_type::way:
                {
                    auto *way = static_cast<osmium::Way *>(entity);
                    if (!m_handler.handle_way(*way)) {
                        m_current = m_type_module.attr("Way")(COSMWay{way});
                        m_current_type = osmium::item_type::way;
                        return m_current;
                    }
                    break;
                }
                case osmium::item_type::relation:
                {
                    auto *rel = static_cast<osmium::Relation *>(entity);
                    if (!m_handler.handle_relation(*rel)) {
                        m_current = m_type_module.attr("Relation")(COSMRelation{rel});
                        m_current_type = osmium::item_type::relation;
                        return m_current;
                    }
                    break;
                }
                case osmium::item_type::area:
                {
                    auto *area = static_cast<osmium::Area *>(entity);
                    if (!m_handler.handle_area(*area)) {
                        m_current = m_type_module.attr("Area")(COSMArea{area});
                        m_current_type = osmium::item_type::area;
                        return m_current;
                    }
                    break;
                }
                case osmium::item_type::changeset:
                {
                    auto *cs = static_cast<osmium::Changeset *>(entity);
                    if (!m_handler.handle_changeset(*cs)) {
                        m_current = m_type_module.attr("Changeset")(COSMChangeset{cs});
                        m_current_type = osmium::item_type::changeset;
                        return m_current;
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
    void invalidate_current()
    {
        switch (m_current_type) {
            case osmium::item_type::node:
                m_current.attr("_pyosmium_data").template cast<COSMNode *>()->invalidate();
                break;
            case osmium::item_type::way:
                m_current.attr("_pyosmium_data").template cast<COSMWay *>()->invalidate();
                break;
            case osmium::item_type::relation:
                m_current.attr("_pyosmium_data").template cast<COSMRelation *>()->invalidate();
                break;
            case osmium::item_type::area:
                m_current.attr("_pyosmium_data").template cast<COSMArea *>()->invalidate();
                break;
            case osmium::item_type::changeset:
                m_current.attr("_pyosmium_data").template cast<COSMChangeset *>()->invalidate();
                break;
        }
        m_current_type = osmium::item_type::undefined;
    }

    HandlerChain m_handler;

    std::queue<osmium::memory::Buffer> m_buffers;
    osmium::memory::Buffer::iterator m_current_it;
    osmium::item_type m_current_type = osmium::item_type::undefined;
    pybind11::object m_current;

    pybind11::object m_type_module = pybind11::module_::import("osmium.osm.types");
};

} // namespace

#endif // PYOSMIUM_BUFFER_ITERATOR_H
