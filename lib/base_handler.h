#ifndef PYOSMIUM_BASE_HANDLER_HPP
#define PYOSMIUM_BASE_HANDLER_HPP

#include <osmium/area/assembler.hpp>
#include <osmium/area/multipolygon_manager.hpp>
#include <osmium/handler.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>
#include <osmium/index/map/all.hpp>

class BaseHandler : public osmium::handler::Handler
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
    virtual ~BaseHandler() = default;
    virtual osmium::osm_entity_bits::type enabled_callbacks() = 0;

    // work around pybind's bad copy policy
    // (see https://github.com/pybind/pybind11/issues/1241)
    void node(const osmium::Node &o) { node(&o); }
    void way(const osmium::Way &o) { way(&o); }
    void relation(const osmium::Relation &o) { relation(&o); }
    void changeset(const osmium::Changeset &o) { changeset(&o); }
    void area(const osmium::Area &o) { area(&o); }

    // actual handler functions
    virtual void node(const osmium::Node*) {}
    virtual void way(const osmium::Way*) {}
    virtual void relation(const osmium::Relation*) {}
    virtual void changeset(const osmium::Changeset*) {}
    virtual void area(const osmium::Area*) {}


private:
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
                      mp_manager.handler([this](const osmium::memory::Buffer &ab)
                                         { osmium::apply(ab, *this); }));
    }

protected:
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

#endif // PYOSMIUM_BASE_HANDLER_HPP
