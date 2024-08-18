/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <vector>

#include <boost/function_output_iterator.hpp>

#include <osmium/osm/object_comparisons.hpp>
#include <osmium/io/any_input.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/io/output_iterator.hpp>
#include <osmium/object_pointer_collection.hpp>
#include <osmium/visitor.hpp>

#include "osmium_module.h"
#include "handler_chain.h"

namespace py = pybind11;

namespace {

    /**
     *  Copy the first OSM object with a given Id to the output. Keep
     *  track of the Id of each object to do this.
     *
     *  We are using this functor class instead of a simple lambda, because the
     *  lambda doesn't build on MSVC.
     */
    class copy_first_with_id {
        osmium::io::Writer* writer;
        osmium::object_id_type id = 0;

    public:
        explicit copy_first_with_id(osmium::io::Writer& w) :
            writer(&w) {
        }

        void operator()(const osmium::OSMObject& obj) {
            if (obj.id() != id) {
                if (obj.visible()) {
                    (*writer)(obj);
                }
                id = obj.id();
            }
        }

    };



class MergeInputReader
{
public:
    void apply_internal(py::args args, bool simplify)
    {
        pyosmium::HandlerChain handler{args};
        if (simplify) {
            objects.sort(osmium::object_order_type_id_reverse_version());
            osmium::item_type prev_type = osmium::item_type::undefined;
            osmium::object_id_type prev_id = 0;
            for (auto &item: objects) {
                if (item.type() != prev_type || item.id() != prev_id) {
                    prev_type = item.type();
                    prev_id = item.id();
                    pyosmium::apply_item(item, handler);
                }
            }
        } else {
            objects.sort(osmium::object_order_type_id_version());
            for (auto &obj : objects) {
                pyosmium::apply_item(obj, handler);
            }
        }

        objects = osmium::ObjectPointerCollection();
        changes.clear();
    }

    void apply_to_reader(osmium::io::Reader &reader, osmium::io::Writer &writer,
                         bool with_history)
    {
        auto input = osmium::io::make_input_iterator_range<osmium::OSMObject>(reader);
        if (with_history) {
            // For history files this is a straightforward sort of the change
            // files followed by a merge with the input file.
            objects.sort(osmium::object_order_type_id_version());

            auto out = osmium::io::make_output_iterator(writer);
            std::set_union(objects.begin(),
                    objects.end(),
                    input.begin(),
                    input.end(),
                    out);
        } else {
            // For normal data files we sort with the largest version of each
            // object first and then only copy this last version of any object
            // to the output.
            // Caution: When change files have been
            // created from extracts it is possible that they contain objects
            // with the same type, id, version, and timestamp. In that case we
            // still want to get the last object available. So we have to make
            // sure it appears first in the objects vector before doing the
            // stable sort.
            std::reverse(objects.ptr_begin(), objects.ptr_end());
            objects.sort(osmium::object_order_type_id_reverse_version());

            auto output_it = boost::make_function_output_iterator(
                    copy_first_with_id(writer)
                    );

            std::set_union(objects.begin(),
                    objects.end(),
                    input.begin(),
                    input.end(),
                    output_it,
                    osmium::object_order_type_id_reverse_version());
        }
    }

    size_t add_file(std::string const &filename)
    { return internal_add(osmium::io::File(filename)); }

    size_t add_buffer(py::buffer const &buf, std::string const &format)
    {
        auto *view = new Py_buffer();
        if (PyObject_GetBuffer(buf.ptr(), view, PyBUF_C_CONTIGUOUS | PyBUF_FORMAT) != 0) {
            delete view;
            throw pybind11::error_already_set();
        }
        pybind11::buffer_info info(view);

        return internal_add(osmium::io::File(reinterpret_cast<char const *>(info.ptr),
                                             static_cast<size_t>(info.size),
                                             format.c_str()));
    }

private:
    size_t internal_add(osmium::io::File change_file)
    {
        size_t sz = 0;

        osmium::io::Reader reader(change_file, osmium::osm_entity_bits::nwr);
        while (osmium::memory::Buffer buffer = reader.read()) {
            osmium::apply(buffer, objects);
            sz += buffer.committed();
            changes.push_back(std::move(buffer));
        }

        return sz;
    }

    std::vector<osmium::memory::Buffer> changes;
    osmium::ObjectPointerCollection objects;
};

} // namespace

namespace pyosmium {

void init_merge_input_reader(py::module &m)
{
    py::class_<MergeInputReader>(m, "MergeInputReader")
        .def(py::init<>())
        .def("_apply_internal", &MergeInputReader::apply_internal,
             py::arg("simplify")=true)
        .def("apply_to_reader", &MergeInputReader::apply_to_reader,
             py::arg("reader"), py::arg("writer"), py::arg("with_history")=false)
        .def("add_file", &MergeInputReader::add_file,
             py::arg("file"))
        .def("add_buffer", &MergeInputReader::add_buffer,
             py::arg("buffer"), py::arg("format"))
    ;
};

} // namespace
