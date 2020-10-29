#include <pybind11/pybind11.h>

#include <osmium/io/any_input.hpp>
#include <osmium/io/any_output.hpp>

namespace py = pybind11;

PYBIND11_MODULE(io, m)
{
    py::class_<osmium::io::File>(m, "File",
        "A data file.")
        .def(py::init<std::string>())
        .def(py::init<std::string, std::string>())
        .def_property("has_multiple_object_versions",
                      &osmium::io::File::has_multiple_object_versions,
                      &osmium::io::File::set_has_multiple_object_versions,
                      "True if there may be more than one version of the same "
                      "object in the file. This happens normally only in history "
                      "files.")
        .def("parse_format", &osmium::io::File::parse_format,
             "Set the format of the file from a format string.")
    ;

    py::class_<osmium::io::Header>(m, "Header",
        "File header with global information about the file.")
        .def(py::init<>())
        .def_property("has_multiple_object_versions",
                      &osmium::io::Header::has_multiple_object_versions,
                      &osmium::io::Header::set_has_multiple_object_versions,
                      "True if there may be more than one version of the same "
                      "object in the file. This happens normally only in history "
                      "files.")
        .def("box", &osmium::io::Header::box,
             "Return the bounding box of the data in the file or an invalid "
             "box if the information is not available.")
        .def("get", &osmium::io::Header::get,
             py::arg("key"), py::arg("default")="",
             "Get the value of header option 'key' or default value if "
             "there is no header option with that name. The default cannot be "
             "None.")
        .def("set",
             (void (osmium::io::Header::*)(const std::string&, const char*))
                 &osmium::io::Header::set,
             py::arg("key"), py::arg("value"),
             "Set the value of header option 'key'.")
    ;

    py::class_<osmium::io::Reader>(m, "Reader",
        "A class that reads OSM data from a file.")
        .def(py::init<std::string>())
        .def(py::init<std::string, osmium::osm_entity_bits::type>())
        .def("eof", &osmium::io::Reader::eof,
             "Check if the end of file has been reached.")
        .def("close", &osmium::io::Reader::close,
             "Close any open file handles. The reader is unusable afterwards.")
        .def("header", &osmium::io::Reader::header,
             "Return the header with file information, see :py:class:`osmium.io.Header`.")
    ;

    py::class_<osmium::io::Writer>(m, "Writer",
        "Class for writing OSM data to a file. This class just encapsulates an "
        "OSM file. Have a look `osmium.SimpleWriter` for a high-level interface "
        "for writing out data.")
        .def(py::init<std::string>())
        .def(py::init<osmium::io::File>())
        .def(py::init<std::string, osmium::io::Header>())
        .def(py::init<osmium::io::File, osmium::io::Header>())
        .def("close", &osmium::io::Writer::close,
             "Close any open file handles. The writer is unusable afterwards.")
    ;
}
