/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#ifndef PYOSMIUM_SIMPLE_HANDLER_HPP
#define PYOSMIUM_SIMPLE_HANDLER_HPP

#include <pybind11/pybind11.h>

#include <osmium/io/any_input.hpp>
#include <osmium/io/file.hpp>
#include <osmium/visitor.hpp>
#include <osmium/area/assembler.hpp>
#include <osmium/area/multipolygon_manager.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>
#include <osmium/index/map/all.hpp>


#include "base_handler.h"
#include "osm_base_objects.h"

class SimpleHandler: public BaseHandler
{
    using IndexType =
        osmium::index::map::Map<osmium::unsigned_object_id_type, osmium::Location>;
    using IndexFactory =
        osmium::index::MapFactory<osmium::unsigned_object_id_type, osmium::Location>;
    using MpManager =
        osmium::area::MultipolygonManager<osmium::area::Assembler>;


protected:
    enum pre_handler {
        no_handler,
        location_handler,
        area_handler
    };


public:
    virtual ~SimpleHandler() = default;
    virtual osmium::osm_entity_bits::type enabled_callbacks() = 0;

    void apply_file(pybind11::object filename, bool locations = false,
                    const std::string &idx = "flex_mem")
    {
        std::string path = pybind11::str(((pybind11::object) filename.attr("__str__"))());
        apply_object(osmium::io::File(path), locations, idx);
    }

    void apply_buffer(pybind11::buffer const &buf, std::string const &format,
                      bool locations = false,
                      const std::string &idx = "flex_mem")
    {
        auto *view = new Py_buffer();
        if (PyObject_GetBuffer(buf.ptr(), view, PyBUF_C_CONTIGUOUS | PyBUF_FORMAT) != 0) {
            delete view;
            throw pybind11::error_already_set();
        }
        pybind11::buffer_info info(view);

        apply_object(osmium::io::File(reinterpret_cast<const char *>(info.ptr),
                                      static_cast<size_t>(info.size), format.c_str()),
                     locations, idx);
    }

private:
    void apply_object(osmium::io::File file, bool locations, const std::string &idx)
    {
        osmium::osm_entity_bits::type entities = osmium::osm_entity_bits::nothing;
        pre_handler handler = locations? location_handler : no_handler;

        auto callbacks = enabled_callbacks();

        if (callbacks & osmium::osm_entity_bits::area)
        {
            entities = osmium::osm_entity_bits::object;
            handler = area_handler;
        } else {
            if (locations || callbacks & osmium::osm_entity_bits::node)
                entities |= osmium::osm_entity_bits::node;
            if (callbacks & osmium::osm_entity_bits::way)
                entities |= osmium::osm_entity_bits::way;
            if (callbacks & osmium::osm_entity_bits::relation)
                entities |= osmium::osm_entity_bits::relation;
        }

        if (callbacks & osmium::osm_entity_bits::changeset)
            entities |= osmium::osm_entity_bits::changeset;

        pybind11::gil_scoped_release release;
        apply(file, entities, handler, idx);
    }


    void apply_with_location(osmium::io::Reader &r, const std::string &idx)
    {
        const auto &map_factory = IndexFactory::instance();
        auto index = map_factory.create_map(idx);
        osmium::handler::NodeLocationsForWays<IndexType> location_handler(*index);
        location_handler.ignore_errors();

        osmium::apply(r, location_handler, *this);
    }

    void apply_with_area(osmium::io::Reader &r, MpManager &mp_manager,
                         const std::string &idx)
    {
        const auto &map_factory = IndexFactory::instance();
        auto index = map_factory.create_map(idx);
        osmium::handler::NodeLocationsForWays<IndexType> location_handler(*index);
        location_handler.ignore_errors();

        osmium::apply(r, location_handler, *this,
                      mp_manager.handler([this](osmium::memory::Buffer &&ab)
                                         { osmium::apply(ab, *this); }));
    }

    void apply(const osmium::io::File &file, osmium::osm_entity_bits::type types,
               pre_handler pre = no_handler,
               const std::string &idx = "flex_mem")
    {
         switch (pre) {
            case no_handler:
                {
                    osmium::io::Reader reader(file, types);
                    osmium::apply(reader, *this);
                    reader.close();
                    break;
                }
            case location_handler:
                {
                    osmium::io::Reader reader(file, types);
                    apply_with_location(reader, idx);
                    reader.close();
                    break;
                }
            case area_handler:
                {
                    osmium::area::Assembler::config_type assembler_config;
                    MpManager mp_manager{assembler_config};

                    osmium::relations::read_relations(file, mp_manager);

                    osmium::io::Reader reader2(file);
                    apply_with_area(reader2, mp_manager, idx);
                    reader2.close();
                    break;
                }
        }
    }
};

template <typename T>
class ObjectGuard {
    using WardPtr = T*;

    public:
        ObjectGuard(pybind11::object ward) : m_ward(ward) {}

        ~ObjectGuard() {
            m_ward.attr("_pyosmium_data").template cast<WardPtr>()->invalidate();
        }

    private:
        pybind11::object m_ward;
};

class PySimpleHandler : public SimpleHandler
{
public:
    using SimpleHandler::SimpleHandler;

    osmium::osm_entity_bits::type enabled_callbacks() override
    {
        auto callbacks = osmium::osm_entity_bits::nothing;
        if (callback("node"))
            callbacks |= osmium::osm_entity_bits::node;
        if (callback("way"))
            callbacks |= osmium::osm_entity_bits::way;
        if (callback("relation"))
            callbacks |= osmium::osm_entity_bits::relation;
        if (callback("area"))
            callbacks |= osmium::osm_entity_bits::area;
        if (callback("changeset"))
            callbacks |= osmium::osm_entity_bits::changeset;

        return callbacks;
    }

    // handler functions
    void node(osmium::Node const *n) override
    {
        pybind11::gil_scoped_acquire acquire;
        auto func = callback("node");
        if (func) {
            auto obj = m_type_module.attr("Node")(COSMNode{n});
            ObjectGuard<COSMNode> guard(obj);
            func(obj);
        }
    }

    void way(osmium::Way *w) override
    {
        pybind11::gil_scoped_acquire acquire;
        auto func = callback("way");
        if (func) {
            auto obj = m_type_module.attr("Way")(COSMWay{w});
            ObjectGuard<COSMWay> guard(obj);
            func(obj);
        }
    }

    void relation(osmium::Relation const *r) override
    {
        pybind11::gil_scoped_acquire acquire;
        auto func = callback("relation");
        if (func) {
            auto obj = m_type_module.attr("Relation")(COSMRelation{r});
            ObjectGuard<COSMRelation> guard(obj);
            func(obj);
        }
    }

    void changeset(osmium::Changeset const *c) override
    {
        pybind11::gil_scoped_acquire acquire;
        auto func = callback("changeset");
        if (func) {
            auto obj = m_type_module.attr("Changeset")(COSMChangeset{c});
            ObjectGuard<COSMChangeset> guard(obj);
            func(obj);
        }
    }

    void area(osmium::Area const *a) override
    {
        pybind11::gil_scoped_acquire acquire;
        auto func = callback("area");
        if (func) {
            auto obj = m_type_module.attr("Area")(COSMArea{a});
            ObjectGuard<COSMArea> guard(obj);
            func(obj);
        }
    }

private:
    pybind11::function callback(char const *name)
    { return pybind11::get_overload(static_cast<SimpleHandler const *>(this), name); }

    pybind11::object m_type_module = pybind11::module_::import("osmium.osm.types");
};

#endif // PYOSMIUM_SIMPLE_HANDLER_HPP
