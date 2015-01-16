#include <boost/python.hpp>

#include <osmium/osm.hpp>
#include <osmium/index/map/all.hpp>

using namespace boost::python;

typedef osmium::index::map::Map<osmium::unsigned_object_id_type, osmium::Location> LocationTable;

LocationTable *create_map(const std::string& config_string) {
    const auto& map_factory = osmium::index::MapFactory<osmium::unsigned_object_id_type, osmium::Location>::instance();
    return map_factory.create_map(config_string).release();
}

std::vector<std::string> map_types() {
    const auto& map_factory = osmium::index::MapFactory<osmium::unsigned_object_id_type, osmium::Location>::instance();
    return map_factory.map_types();
}

BOOST_PYTHON_MODULE(_index)
{
    class_<LocationTable, boost::noncopyable>("LocationTable", no_init)
        .def("set", &LocationTable::set)
        .def("get", &LocationTable::get)
        .def("size", &LocationTable::size)
        .def("used_memory", &LocationTable::used_memory)
        .def("clear", &LocationTable::clear)
    ;

    def("create_map", &create_map, return_value_policy<manage_new_object>());
    def("map_types", &map_types);
}

