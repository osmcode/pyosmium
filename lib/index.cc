#include <boost/python.hpp>

#include <osmium/osm.hpp>
#include <osmium/index/map/all.hpp>
#include <osmium/index/node_locations_map.hpp>

#include "win_boost_fix.hpp"

using namespace boost::python;

typedef osmium::index::map::Map<osmium::unsigned_object_id_type, osmium::Location> LocationTable;

LocationTable *create_map(const std::string& config_string) {
    const auto& map_factory = osmium::index::MapFactory<osmium::unsigned_object_id_type, osmium::Location>::instance();
    return map_factory.create_map(config_string).release();
}

PyObject *map_types() {
    const auto& map_factory = osmium::index::MapFactory<osmium::unsigned_object_id_type, osmium::Location>::instance();

    boost::python::list* l = new boost::python::list();
    for (auto const &e : map_factory.map_types())
        (*l).append(e);

    return l->ptr();
}

BOOST_PYTHON_MODULE(index)
{
    docstring_options doc_options(true, true, false);

    class_<LocationTable, boost::noncopyable>("LocationTable",
        "A map from a node ID to a location object. This implementation works "
        "only with positive node IDs.",
        no_init)
        .def("set", &LocationTable::set,
             (arg("self"), arg("id"), arg("loc")),
             "Set the location for a given node id.")
        .def("get", &LocationTable::get,
             (arg("self"), arg("id")),
             "Return the location for a given id.")
        .def("used_memory", &LocationTable::used_memory,
             arg("self"),
             "Return the size (in bytes) currently allocated by this location table.")
        .def("clear", &LocationTable::clear,
             arg("self"),
             "Remove all entries from the location table.")
    ;

    def("create_map", &create_map, return_value_policy<manage_new_object>(),
        (arg("map_type")),
        "Create a new location store. The string parameter takes the type "
        "and, where required, additional arguments separated by comma. For "
        "example, to create an array cache backed by a file ``foo.store``, "
        "the map_type should be ``dense_file_array,foo.store``.");
    def("map_types", &map_types,
        "Return a list of strings with valid types for the location table.");
}

