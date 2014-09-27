#include <boost/python.hpp>

#include <osmium/io/any_input.hpp>

#include "osm.cc"

BOOST_PYTHON_MODULE(_io)
{
    using namespace boost::python;

    class_<osmium::io::Reader, boost::noncopyable>("Reader", init<std::string>())
        .def(init<std::string, osmium::osm_entity_bits::type>())
        .def("eof", &osmium::io::Reader::eof)
    ;

}
