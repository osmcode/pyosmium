/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2025 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>
#include <pybind11/stl/filesystem.h>

#include <osmium/io/any_input.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/thread/pool.hpp>

#include <filesystem>

#include "io.h"

namespace py = pybind11;

namespace {

class FileBuffer : public osmium::io::File
{
    using osmium::io::File::File;
};

} // namespace


#ifdef Py_GIL_DISABLED
PYBIND11_MODULE(io, m, py::mod_gil_not_used())
#else
PYBIND11_MODULE(io, m)
#endif
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

    py::class_<pyosmium::PyReader>(m, "Reader")
        .def(py::init<osmium::io::File, osmium::osm_entity_bits::type const *,
                      osmium::thread::Pool *>(),
             py::keep_alive<1, 2>(), py::keep_alive<1, 4>(),
             py::arg("file"), py::arg("types") = nullptr, py::arg("thread_pool") = nullptr
            )
        .def(py::init<>([] (std::string file,
                            osmium::osm_entity_bits::type const *types,
                            osmium::thread::Pool *pool) {
                 return new pyosmium::PyReader(osmium::io::File(std::move(file)),
                                               types, pool); }),
             py::keep_alive<1, 2>(), py::keep_alive<1, 4>(),
             py::arg("file"), py::arg("types") = nullptr, py::arg("thread_pool") = nullptr
            )
        .def(py::init<>([] (std::filesystem::path const &file,
                            osmium::osm_entity_bits::type const *types,
                            osmium::thread::Pool *pool) {
                 return new pyosmium::PyReader(osmium::io::File(file.string()),
                                               types, pool); }),
             py::keep_alive<1, 2>(), py::keep_alive<1, 4>(),
             py::arg("file"), py::arg("types") = nullptr, py::arg("thread_pool") = nullptr
            )
        .def("eof", [](pyosmium::PyReader const &self) { return self.get()->eof(); })
        .def("close", [](pyosmium::PyReader &self) { self.get()->close(); })
        .def("header", [](pyosmium::PyReader &self) { return self.get()->header(); })
        .def("__enter__", [](py::object const &self) { return self; })
        .def("__exit__", [](pyosmium::PyReader &self, py::args args) { self.get()->close(); })
    ;

    py::class_<pyosmium::PyWriter>(m, "Writer")
        .def(py::init<osmium::io::File, osmium::io::Header const *, bool, osmium::thread::Pool *>(),
             py::keep_alive<1, 5>(),
             py::arg("file"), py::arg("header") = nullptr,
             py::arg("overwrite") = false, py::arg("thread_pool") = nullptr
            )
        .def(py::init<>([] (std::filesystem::path const &file, osmium::io::Header const *header,
                            bool overwrite, osmium::thread::Pool *pool) {
                 return new pyosmium::PyWriter(osmium::io::File(file.string()),
                                               header, overwrite, pool); }),
             py::keep_alive<1, 5>(),
             py::arg("file"), py::arg("header") = nullptr,
             py::arg("overwrite") = false, py::arg("thread_pool") = nullptr
            )
        .def(py::init<>([] (std::string filename, osmium::io::Header const *header,
                            bool overwrite, osmium::thread::Pool *pool) {
                 return new pyosmium::PyWriter(osmium::io::File(std::move(filename)),
                                               header, overwrite, pool); }),
             py::keep_alive<1, 5>(),
             py::arg("file"), py::arg("header") = nullptr,
             py::arg("overwrite") = false, py::arg("thread_pool") = nullptr
            )
        .def("close", [](pyosmium::PyWriter &self) { self.get()->close(); })
    ;

    py::class_<osmium::thread::Pool>(m, "ThreadPool")
        .def(py::init<int, std::size_t>(),
             py::arg("num_threads")=0, py::arg("max_queue_size")=0U)
        .def_property_readonly("num_threads", &osmium::thread::Pool::num_threads)
        .def("queue_size", &osmium::thread::Pool::queue_size)
        .def("queue_empty", &osmium::thread::Pool::queue_empty)
     ;
}
