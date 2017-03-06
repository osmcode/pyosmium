#include <boost/python.hpp>

#include <osmium/io/any_input.hpp>
#include <osmium/io/any_output.hpp>

#include "osm.cc"

BOOST_PYTHON_MODULE(io)
{
    using namespace boost::python;
    docstring_options doc_options(true, true, false);

    class_<osmium::io::Header>("Header",
        "File header with global information about the file.")
        .add_property("has_multiple_object_versions",
                      &osmium::io::Header::has_multiple_object_versions,
                      make_function(&osmium::io::Header::set_has_multiple_object_versions, return_value_policy<reference_existing_object>()),
                      "True if there may be more than one version of the same "
                      "object in the file. This happens normally only in history "
                      "files.")
        .def("box", &osmium::io::Header::box, arg("self"),
                "Return the bounding box of the data in the file or an invalid "
                "box if the information is not available.")
        .def("get", &osmium::io::Header::get, (arg("self"), arg("key"), arg("default")=""),
                "Get the value of header option 'key' or default value if "
                "there is no header option with that name. The default cannot be "
                "None.")
        .def("set", static_cast<void (osmium::io::Header::*)(const std::string&, const char*)>(&osmium::io::Header::set),
                (arg("self"), arg("key"), arg("value")),
                "Set the value of header option 'key'.")
    ;

    class_<osmium::io::Reader, boost::noncopyable>("Reader",
        "A class that reads OSM data from a file.",
        init<std::string>())
        .def(init<std::string, osmium::osm_entity_bits::type>())
        .def("eof", &osmium::io::Reader::eof, arg("self"),
             "Check if the end of file has been reached.")
        .def("close", &osmium::io::Reader::close, arg("self"),
             "Close any open file handles. The reader is unusable afterwards.")
        .def("header", &osmium::io::Reader::header, arg("self"),
             "Return the header with file information, see :py:class:`osmium.io.Header`.")
    ;

    class_<osmium::io::Writer, boost::noncopyable>("Writer",
        "Class for writing OSM data to a file. This class just encapsulates an "
        "OSM file,. Have a look `osmium.SimpleWriter` for a high-level interface "
        "for writing out data.",
        init<std::string>())
        .def(init<std::string, osmium::io::Header>())
        .def("close", &osmium::io::Writer::close, arg("self"),
             "Close any open file handles. The writer is unusable afterwards.")
    ;
}
