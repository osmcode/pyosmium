#ifndef PYOSMIUM_SIMPLE_HANDLER_HPP
#define PYOSMIUM_SIMPLE_HANDLER_HPP

#include <pybind11/pybind11.h>

#include <osmium/io/any_input.hpp>
#include <osmium/io/file.hpp>
#include <osmium/visitor.hpp>

#include "base_handler.h"
#include "osm_wrapper.h"

class SimpleHandler: public BaseHandler
{
public:
    virtual ~SimpleHandler() = default;

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
        BaseHandler::pre_handler handler = locations?
                                            BaseHandler::location_handler
                                            :BaseHandler::no_handler;

        auto callbacks = enabled_callbacks();

        if (callbacks & osmium::osm_entity_bits::area)
        {
            entities = osmium::osm_entity_bits::object;
            handler = BaseHandler::area_handler;
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
            func(obj);
            obj.attr("_data").cast<COSMNode *>()->invalidate();
        }
    }

    void way(osmium::Way const *w) override
    {
        pybind11::gil_scoped_acquire acquire;
        auto func = callback("way");
        if (func) {
            auto obj = m_type_module.attr("Way")(COSMWay{w});
            func(obj);
            obj.attr("_data").cast<COSMWay *>()->invalidate();
        }
    }

    void relation(osmium::Relation const *r) override
    {
        pybind11::gil_scoped_acquire acquire;
        auto func = callback("relation");
        if (func) {
            auto obj = m_type_module.attr("Relation")(COSMRelation{r});
            func(obj);
            obj.attr("_data").cast<COSMRelation *>()->invalidate();
        }
    }

    void changeset(osmium::Changeset const *c) override
    {
        pybind11::gil_scoped_acquire acquire;
        auto func = callback("changeset");
        if (func) {
            auto obj = m_type_module.attr("Changeset")(COSMChangeset{c});
            func(obj);
            obj.attr("_data").cast<COSMChangeset *>()->invalidate();
        }
    }

    void area(osmium::Area const *a) override
    {
        pybind11::gil_scoped_acquire acquire;
        auto func = callback("area");
        if (func) {
            auto obj = m_type_module.attr("Area")(COSMArea{a});
            func(obj);
            obj.attr("_data").cast<COSMArea *>()->invalidate();
        }
    }

private:
    pybind11::function callback(char const *name)
    { return pybind11::get_overload(static_cast<SimpleHandler const *>(this), name); }

    pybind11::object m_type_module = pybind11::module_::import("osmium.osm.types");
};

#endif // PYOSMIUM_SIMPLE_HANDLER_HPP
