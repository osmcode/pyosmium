#include <boost/python.hpp>

#include <osmium/io/any_input.hpp>

BOOST_PYTHON_MODULE(_io)
{
    using namespace boost::python;

    class_<osmium::io::Reader, boost::noncopyable>("Reader", init<std::string>())
        .def("eof", &osmium::io::Reader::eof)
    ;

}
