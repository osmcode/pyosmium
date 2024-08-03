/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <osmium/io/any_input.hpp>
#include <osmium/io/file.hpp>

#include "osmium_module.h"
#include "osm_base_objects.h"
#include "handler_chain.h"

namespace py = pybind11;

namespace {

class OsmFileIterator
{
public:
    OsmFileIterator(osmium::io::Reader *reader, py::args args)
    : m_reader(reader), m_pre_handler(args)
    {
        m_buffer = m_reader->read();

        if (m_buffer) {
            m_buffer_it = m_buffer.begin();
        }
    }


    ~OsmFileIterator()
    {
        invalidate_current();
    }

    pybind11::object next()
    {
        while (true) {
            invalidate_current();

            if (!m_buffer) {
                throw pybind11::stop_iteration();
            }

            while (m_buffer_it == m_buffer.end()) {
                m_buffer = m_reader->read();
                if (!m_buffer) {
                    m_pre_handler.flush();
                    throw pybind11::stop_iteration();
                }
                m_buffer_it = m_buffer.begin();
            }

            osmium::OSMEntity *entity = &*m_buffer_it;
            ++m_buffer_it;

            switch (entity->type()) {
                case osmium::item_type::node:
                {
                    auto *node = static_cast<osmium::Node *>(entity);
                    if (!m_pre_handler.handle_node(*node)) {
                        m_current = m_type_module.attr("Node")(pyosmium::COSMNode{node});
                        m_current_type = osmium::item_type::node;
                        return m_current;
                    }
                    break;
                }
                case osmium::item_type::way:
                {
                    auto *way = static_cast<osmium::Way *>(entity);
                    if (!m_pre_handler.handle_way(*way)) {
                        m_current = m_type_module.attr("Way")(pyosmium::COSMWay{way});
                        m_current_type = osmium::item_type::way;
                        return m_current;
                    }
                    break;
                }
                case osmium::item_type::relation:
                {
                    auto *rel = static_cast<osmium::Relation *>(entity);
                    if (!m_pre_handler.handle_relation(*rel)) {
                        m_current = m_type_module.attr("Relation")(pyosmium::COSMRelation{rel});
                        m_current_type = osmium::item_type::relation;
                        return m_current;
                    }
                    break;
                }
                case osmium::item_type::changeset:
                {
                    auto *cs = static_cast<osmium::Changeset *>(entity);
                    if (!m_pre_handler.handle_changeset(*cs)) {
                        m_current = m_type_module.attr("Changeset")(pyosmium::COSMChangeset{cs});
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
                m_current.attr("_pyosmium_data").template cast<pyosmium::COSMNode *>()->invalidate();
                break;
            case osmium::item_type::way:
                m_current.attr("_pyosmium_data").template cast<pyosmium::COSMWay *>()->invalidate();
                break;
            case osmium::item_type::relation:
                m_current.attr("_pyosmium_data").template cast<pyosmium::COSMRelation *>()->invalidate();
                break;
            case osmium::item_type::changeset:
                m_current.attr("_pyosmium_data").template cast<pyosmium::COSMChangeset *>()->invalidate();
                break;
        }
        m_current_type = osmium::item_type::undefined;
    }

    osmium::io::Reader *m_reader;
    osmium::memory::Buffer m_buffer;
    osmium::memory::Buffer::iterator m_buffer_it;
    osmium::item_type m_current_type = osmium::item_type::undefined;
    pybind11::object m_current;

    pyosmium::HandlerChain m_pre_handler;

    pybind11::object m_type_module = pybind11::module_::import("osmium.osm.types");
};

} // namespace

namespace pyosmium {

void init_osm_file_iterator(py::module &m)
{
    py::class_<OsmFileIterator>(m, "OsmFileIterator",
        "Iterator interface for reading an OSM file.")
        .def(py::init<osmium::io::Reader *, py::args>())
        .def("__iter__", [](py::object const &self) { return self; })
        .def("__next__", &OsmFileIterator::next,
             "Get the next OSM object from the file or raise a StopIteration.")
        ;
}

} // namespace
