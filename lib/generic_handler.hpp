#ifndef PYOSMIUM_GENERIC_HANDLER_HPP
#define PYOSMIUM_GENERIC_HANDLER_HPP

#include <osmium/area/assembler.hpp>
#include <osmium/area/multipolygon_manager.hpp>
#include <osmium/handler.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>
#include <osmium/index/map/all.hpp>
#include <osmium/io/any_input.hpp>
#include <osmium/io/file.hpp>
#include <osmium/visitor.hpp>

#include <boost/python.hpp>


typedef osmium::index::map::Map<osmium::unsigned_object_id_type, osmium::Location> index_type;

class BaseHandler : public osmium::handler::Handler {

protected:
    enum pre_handler {
        no_handler,
        location_handler,
        area_handler
    };

public:
virtual void apply_start() {};
// handler functions
virtual void node(const osmium::Node&) = 0;
virtual void way(const osmium::Way&) = 0;
virtual void relation(const osmium::Relation&) = 0;
virtual void changeset(const osmium::Changeset&) = 0;
virtual void area(const osmium::Area&) = 0;


private:
void apply_with_location(osmium::io::Reader &r, const std::string &idx) {
    const auto& map_factory = osmium::index::MapFactory<osmium::unsigned_object_id_type, osmium::Location>::instance();
    std::unique_ptr<index_type> index = map_factory.create_map(idx);
    osmium::handler::NodeLocationsForWays<index_type> location_handler(*index);
    location_handler.ignore_errors();
    osmium::apply(r, location_handler, *this);
}

void apply_with_area(osmium::io::Reader &r,
                     osmium::area::MultipolygonManager<osmium::area::Assembler> &mp_manager,
                     const std::string &idx) {
    const auto& map_factory = osmium::index::MapFactory<osmium::unsigned_object_id_type, osmium::Location>::instance();
    std::unique_ptr<index_type> index = map_factory.create_map(idx);
    osmium::handler::NodeLocationsForWays<index_type> location_handler(*index);
    location_handler.ignore_errors();

    osmium::apply(r, location_handler, *this,
                  mp_manager.handler([this](const osmium::memory::Buffer& area_buffer) {
                       osmium::apply(area_buffer, *this);
                  })
                 );
}


protected:
void apply(const osmium::io::File &file, osmium::osm_entity_bits::type types,
           pre_handler pre = no_handler,
           const std::string &idx = "sparse_mem_array") {

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
            osmium::area::MultipolygonManager<osmium::area::Assembler> mp_manager{assembler_config};

            osmium::relations::read_relations(file, mp_manager);

            osmium::io::Reader reader2(file);
            apply_with_area(reader2, mp_manager, idx);
            reader2.close();
            break;
        }
    }
}



};

using namespace boost::python;

struct SimpleHandlerWrap: BaseHandler, wrapper<BaseHandler> {

    void node(const osmium::Node& node) override {
        if (!(m_callbacks & osmium::osm_entity_bits::node))
            return;

        if (override f = this->get_override("node")) {
            f(boost::ref(node));
        }
    }

    void way(const osmium::Way& way) {
        if (!(m_callbacks & osmium::osm_entity_bits::way))
            return;

        if (override f = this->get_override("way"))
            f(boost::ref(way));
    }

    void relation(const osmium::Relation& rel) {
        if (!(m_callbacks & osmium::osm_entity_bits::relation))
            return;

        if (override f = this->get_override("relation"))
            f(boost::ref(rel));
    }

    void changeset(const osmium::Changeset& cs) {
        if (!(m_callbacks & osmium::osm_entity_bits::changeset))
            return;

        if (override f = this->get_override("changeset"))
            f(boost::ref(cs));
    }

    void area(const osmium::Area& area) {
        if (!(m_callbacks & osmium::osm_entity_bits::area))
            return;

        if (override f = this->get_override("area"))
            f(boost::ref(area));
    }

    void apply_file(const std::string &filename, bool locations = false,
                    const std::string &idx = "sparse_mem_array")
    {
        apply_object(osmium::io::File(filename), locations, idx);
    }

    void apply_buffer(const boost::python::object &buf, const boost::python::str &format,
                      bool locations = false,
                      const std::string &idx = "sparse_mem_array")
    {
        Py_buffer pybuf;
        PyObject_GetBuffer(buf.ptr(), &pybuf, PyBUF_C_CONTIGUOUS);
        size_t len = (size_t) pybuf.len;
        const char *cbuf = reinterpret_cast<const char *>(pybuf.buf);
        const char *cfmt = boost::python::extract<const char *>(format);

        apply_object(osmium::io::File(cbuf, len, cfmt), locations, idx);
    }

    void apply_start() override {
        m_callbacks = osmium::osm_entity_bits::nothing;
        if (hasfunc("node"))
            m_callbacks |= osmium::osm_entity_bits::node;
        if (hasfunc("way"))
            m_callbacks |= osmium::osm_entity_bits::way;
        if (hasfunc("relation"))
            m_callbacks |= osmium::osm_entity_bits::relation;
        if (hasfunc("area"))
            m_callbacks |= osmium::osm_entity_bits::area;
        if (hasfunc("changeset"))
            m_callbacks |= osmium::osm_entity_bits::changeset;
    }


private:
    void apply_object(osmium::io::File file, bool locations, const std::string &idx)
    {
        osmium::osm_entity_bits::type entities = osmium::osm_entity_bits::nothing;
        BaseHandler::pre_handler handler = locations?
                                            BaseHandler::location_handler
                                            :BaseHandler::no_handler;

        apply_start();

        if (m_callbacks & osmium::osm_entity_bits::area)
        {
            entities = osmium::osm_entity_bits::object;
            handler = BaseHandler::area_handler;
        } else {
            if (locations || m_callbacks & osmium::osm_entity_bits::node)
                entities |= osmium::osm_entity_bits::node;
            if (m_callbacks & osmium::osm_entity_bits::way)
                entities |= osmium::osm_entity_bits::way;
            if (m_callbacks & osmium::osm_entity_bits::relation)
                entities |= osmium::osm_entity_bits::relation;
        }

        if (m_callbacks & osmium::osm_entity_bits::changeset)
            entities |= osmium::osm_entity_bits::changeset;

        apply(file, entities, handler, idx);
    }


    bool hasfunc(char const *name) {
        reference_existing_object::apply<SimpleHandlerWrap*>::type converter;
        PyObject* obj = converter( this );

        if (PyObject_HasAttrString(obj, name)) {
            auto o = boost::python::object(handle<>(obj));
            return o.attr(name) != boost::python::object();
        }

        return false;
    }

    osmium::osm_entity_bits::type m_callbacks;
};

#endif
