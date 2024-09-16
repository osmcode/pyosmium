/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>
#include <pybind11/stl/filesystem.h>

#include <osmium/io/any_input.hpp>
#include <osmium/io/any_output.hpp>

#include <filesystem>

namespace py = pybind11;

namespace {

class FileBuffer : public osmium::io::File
{
    using osmium::io::File::File;
};

} // namespace


PYBIND11_MODULE(io, m)
{
    py::class_<osmium::io::File>(m, "File")
        .def(py::init<std::string>())
        .def(py::init<std::string, std::string>())
        .def(py::init<>([] (std::filesystem::path const &file) {
                 return new osmium::io::File(file.string());
             }))
        .def(py::init<>([] (std::filesystem::path const &file, const char *format) {
                 return new osmium::io::File(file.string(), format);
             }))
        .def_property("has_multiple_object_versions",
                      &osmium::io::File::has_multiple_object_versions,
                      &osmium::io::File::set_has_multiple_object_versions)
        .def("parse_format", &osmium::io::File::parse_format)
    ;


    py::class_<FileBuffer, osmium::io::File>(m, "FileBuffer")
        .def(py::init<>([] (py::buffer const &buf, std::string const &format) {
                 pybind11::buffer_info info = buf.request();
                 return new FileBuffer(reinterpret_cast<const char *>(info.ptr),
                                       static_cast<size_t>(info.size), format.c_str());
             }), py::keep_alive<1, 2>())
        .def_property("has_multiple_object_versions",
                      &osmium::io::File::has_multiple_object_versions,
                      &osmium::io::File::set_has_multiple_object_versions)
        .def("parse_format", &osmium::io::File::parse_format)
    ;


    py::class_<osmium::io::Header>(m, "Header")
        .def(py::init<>())
        .def_property("has_multiple_object_versions",
                      &osmium::io::Header::has_multiple_object_versions,
                      &osmium::io::Header::set_has_multiple_object_versions)
        .def("box", &osmium::io::Header::box)
        .def("get", (std::string (osmium::io::Header::*)(std::string const &, std::string const &))
                     &osmium::io::Header::get,
             py::arg("key"), py::arg("default")="")
        .def("set",
             (void (osmium::io::Header::*)(const std::string&, const char*))
                 &osmium::io::Header::set,
             py::arg("key"), py::arg("value"))
        .def("add_box", &osmium::io::Header::add_box,
             py::arg("box"),
             py::return_value_policy::reference_internal)
    ;

    py::class_<osmium::io::Reader>(m, "Reader")
        .def(py::init<std::string>())
        .def(py::init<std::string, osmium::osm_entity_bits::type>())
        .def(py::init<>([] (std::filesystem::path const &file) {
                 return new osmium::io::Reader(file.string());
             }))
        .def(py::init<>([] (std::filesystem::path const &file, osmium::osm_entity_bits::type etype) {
                 return new osmium::io::Reader(file.string(), etype);
             }))
        .def(py::init<osmium::io::File>(),
             py::keep_alive<1, 2>())
        .def(py::init<osmium::io::File, osmium::osm_entity_bits::type>(),
             py::keep_alive<1, 2>())
        .def("eof", &osmium::io::Reader::eof)
        .def("close", &osmium::io::Reader::close)
        .def("header", &osmium::io::Reader::header)
        .def("__enter__", [](py::object const &self) { return self; })
        .def("__exit__", [](osmium::io::Reader &self, py::args args) { self.close(); })
    ;

    py::class_<osmium::io::Writer>(m, "Writer")
        .def(py::init<std::string>())
        .def(py::init<>([] (std::filesystem::path const &file) {
                 return new osmium::io::Writer(file.string());
             }))
        .def(py::init<osmium::io::File>())
        .def(py::init<std::string, osmium::io::Header>())
        .def(py::init<osmium::io::File, osmium::io::Header>())
        .def("close", &osmium::io::Writer::close)
    ;
}
