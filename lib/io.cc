#include <boost/python.hpp>

#include <osmium/io/any_input.hpp>

#include "osm.cc"

BOOST_PYTHON_MODULE(_io)
{
    using namespace boost::python;

    class_<osmium::io::Header>("Header")
        .add_property("has_multiple_object_versions",
                      &osmium::io::Header::has_multiple_object_versions,
                      make_function(&osmium::io::Header::set_has_multiple_object_versions, return_value_policy<reference_existing_object>()))
    ;

    class_<osmium::io::Reader, boost::noncopyable>("Reader", init<std::string>())
        .def(init<std::string, osmium::osm_entity_bits::type>())
        .def("eof", &osmium::io::Reader::eof)
        .def("close", &osmium::io::Reader::close)
        .def("header", &osmium::io::Reader::header)
    ;

}
