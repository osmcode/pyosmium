#ifndef PYOSMIUM_SIMPLE_HANDLER_HPP
#define PYOSMIUM_SIMPLE_HANDLER_HPP

#include <pybind11/pybind11.h>

#include <osmium/io/any_input.hpp>
#include <osmium/io/file.hpp>
#include <osmium/visitor.hpp>

#include "base_handler.h"

class SimpleHandler: public BaseHandler
{
public:
    virtual ~SimpleHandler() = default;

    void apply_file(const std::string &filename, bool locations = false,
                    const std::string &idx = "flex_mem")
    {
        apply_object(osmium::io::File(filename), locations, idx);
    }

    void apply_buffer(pybind11::buffer const &buf, std::string const &format,
                      bool locations = false,
                      const std::string &idx = "flex_mem")
    {
        Py_buffer pybuf;
        PyObject_GetBuffer(buf.ptr(), &pybuf, PyBUF_C_CONTIGUOUS);

        apply_object(osmium::io::File(reinterpret_cast<const char *>(pybuf.buf),
                                      (size_t) pybuf.len, format.c_str()),
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
        if (hasfunc("node"))
            callbacks |= osmium::osm_entity_bits::node;
        if (hasfunc("way"))
            callbacks |= osmium::osm_entity_bits::way;
        if (hasfunc("relation"))
            callbacks |= osmium::osm_entity_bits::relation;
        if (hasfunc("area"))
            callbacks |= osmium::osm_entity_bits::area;
        if (hasfunc("changeset"))
            callbacks |= osmium::osm_entity_bits::changeset;

        return callbacks;
    }

    // handler functions
    void node(osmium::Node const *n) override
    {
        pybind11::gil_scoped_acquire acquire;
        PYBIND11_OVERLOAD(void, SimpleHandler, node, n);
    }

    void way(osmium::Way const *w) override
    {
        pybind11::gil_scoped_acquire acquire;
        PYBIND11_OVERLOAD(void, SimpleHandler, way, w);
    }

    void relation(osmium::Relation const *r) override
    {
        pybind11::gil_scoped_acquire acquire;
        PYBIND11_OVERLOAD(void, SimpleHandler, relation, r);
    }

    void changeset(osmium::Changeset const *c) override
    {
        pybind11::gil_scoped_acquire acquire;
        PYBIND11_OVERLOAD(void, SimpleHandler, changeset, c);
    }

    void area(osmium::Area const *a) override
    {
        pybind11::gil_scoped_acquire acquire;
        PYBIND11_OVERLOAD(void, SimpleHandler, area, a);
    }

private:
    bool hasfunc(char const *name)
    { return (bool)pybind11::get_overload(static_cast<SimpleHandler const *>(this), name); }
};

#endif // PYOSMIUM_SIMPLE_HANDLER_HPP
