#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>
#include <osmium/index/map/all.hpp>
#include <osmium/index/node_locations_map.hpp>

namespace py = pybind11;

PYBIND11_MODULE(index, m)
{
    using LocationTable =
        osmium::index::map::Map<osmium::unsigned_object_id_type, osmium::Location>;
    using IndexFactory =
        osmium::index::MapFactory<osmium::unsigned_object_id_type, osmium::Location>;

    py::class_<LocationTable>(m, "LocationTable",
        "A map from a node ID to a location object. This implementation works "
        "only with positive node IDs.")
        .def("set", &LocationTable::set, py::arg("id"), py::arg("loc"),
             "Set the location for a given node id.")
        .def("get", &LocationTable::get, py::arg("id"),
             "Return the location for a given id.")
        .def("used_memory", &LocationTable::used_memory,
             "Return the size (in bytes) currently allocated by this location table.")
        .def("clear", &LocationTable::clear,
             "Remove all entries from the location table.")
    ;

    m.def("create_map", [](const std::string& config_string) {
            const auto& map_factory = IndexFactory::instance();
            return map_factory.create_map(config_string);
        },
        py::arg("map_type"),
        "Create a new location store. The string parameter takes the type "
        "and, where required, additional arguments separated by comma. For "
        "example, to create an array cache backed by a file ``foo.store``, "
        "the map_type should be ``dense_file_array,foo.store``.");

    m.def("map_types", []() {
        const auto& map_factory = IndexFactory::instance();

        auto l = py::list();
        for (auto const &e : map_factory.map_types())
            l.append(e);

        return l;
        },
        "Return a list of strings with valid types for the location table.");
}
