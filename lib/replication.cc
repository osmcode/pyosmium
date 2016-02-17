#include <osmium/osm.hpp>
#include <osmium/io/any_input.hpp>
#include <osmium/handler.hpp>
#include <osmium/visitor.hpp>

#include <boost/python.hpp>

namespace pyosmium {

struct LastChangeHandler : public osmium::handler::Handler {
    osmium::Timestamp last_change;

    void osm_object(const osmium::OSMObject& obj) {
        set(obj.timestamp());
    }

private:
    void set(const osmium::Timestamp& ts) {
        if (ts > last_change)
            last_change = ts;
    }
};

osmium::Timestamp compute_latest_change(const char* filename)
{
    osmium::io::Reader reader(filename, osmium::osm_entity_bits::node |
                                        osmium::osm_entity_bits::way |
                                        osmium::osm_entity_bits::relation);

    LastChangeHandler handler;
    osmium::apply(reader, handler);
    reader.close();

    return handler.last_change;
}


}

BOOST_PYTHON_MODULE(_replication)
{
    using namespace boost::python;
    def("newest_change_from_file", &pyosmium::compute_latest_change,
        "Find the date of the newest change in a file");
}
