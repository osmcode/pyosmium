#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>
#include <osmium/io/any_input.hpp>
#include <osmium/handler.hpp>
#include <osmium/visitor.hpp>
#include "cast.h"

namespace py = pybind11;

struct LastChangeHandler : public osmium::handler::Handler
{
    osmium::Timestamp last_change;

    void osm_object(osmium::OSMObject const &obj)
    {
        if (obj.timestamp() > last_change) {
            last_change = obj.timestamp();
        }
    }
};


PYBIND11_MODULE(_replication, m)
{
    m.def("newest_change_from_file", [](char const *filename)
        {
            osmium::io::Reader reader(filename, osmium::osm_entity_bits::nwr);

            LastChangeHandler handler;
            osmium::apply(reader, handler);
            reader.close();

            return handler.last_change;
        },
        "Find the date of the most recent change in a file.");
}
