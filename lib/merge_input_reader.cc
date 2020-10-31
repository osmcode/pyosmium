#include <pybind11/pybind11.h>

#include <vector>

#include <boost/function_output_iterator.hpp>

#include <osmium/osm/object_comparisons.hpp>
#include <osmium/io/any_input.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/io/output_iterator.hpp>
#include <osmium/handler.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>
#include <osmium/index/map/all.hpp>
#include <osmium/object_pointer_collection.hpp>
#include <osmium/visitor.hpp>

#include "base_handler.h"
#include "osmium_module.h"

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
    void apply(BaseHandler& handler, std::string const &idx, bool simplify)
    {
        if (idx.empty())
            apply_without_location(handler, simplify);
        else
            apply_with_location(handler, idx, simplify);
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
        Py_buffer pybuf;
        PyObject_GetBuffer(buf.ptr(), &pybuf, PyBUF_C_CONTIGUOUS);

        return internal_add(osmium::io::File(reinterpret_cast<char const *>(pybuf.buf),
                                             (size_t) pybuf.len,
                                             format.c_str()));
    }

private:
    void apply_without_location(BaseHandler& handler, bool simplify)
    {
        if (simplify) {
            objects.sort(osmium::object_order_type_id_reverse_version());
            osmium::item_type prev_type = osmium::item_type::undefined;
            osmium::object_id_type prev_id = 0;
            for (const auto &item: objects) {
                if (item.type() != prev_type || item.id() != prev_id) {
                    prev_type = item.type();
                    prev_id = item.id();
                    osmium::apply_item(item, handler);
                }
            }
        } else {
            objects.sort(osmium::object_order_type_id_version());
            osmium::apply(objects.cbegin(), objects.cend(), handler);
        }

        objects = osmium::ObjectPointerCollection();
        changes.clear();
    }

    void apply_with_location(BaseHandler& handler, std::string const &idx,
                             bool simplify)
    {
        using Index_fab =
            osmium::index::MapFactory<osmium::unsigned_object_id_type, osmium::Location>;
        using Index_type =
            osmium::index::map::Map<osmium::unsigned_object_id_type, osmium::Location>;
        auto index = Index_fab::instance().create_map(idx);
        osmium::handler::NodeLocationsForWays<Index_type> location_handler(*index);
        location_handler.ignore_errors();

        if (simplify) {
            objects.sort(osmium::object_order_type_id_reverse_version());
            osmium::item_type prev_type = osmium::item_type::undefined;
            osmium::object_id_type prev_id = 0;
            for (auto &item: objects) {
                if (item.type() != prev_type || item.id() != prev_id) {
                    prev_type = item.type();
                    prev_id = item.id();
                    osmium::apply_item(item, location_handler, handler);
                }
            }
        } else {
            objects.sort(osmium::object_order_type_id_version());
            osmium::apply(objects.begin(), objects.end(), location_handler, handler);
        }

        objects = osmium::ObjectPointerCollection();
        changes.clear();
    }

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

}

void init_merge_input_reader(py::module &m)
{
    py::class_<MergeInputReader>(m, "MergeInputReader",
        "Collects data from multiple input files, sorts and optionally "
        "deduplicates the data before applying it to a handler.")
        .def(py::init<>())
        .def("apply", &MergeInputReader::apply,
             py::arg("handler"), py::arg("idx")="", py::arg("simplify")=true,
             "Apply collected data to a handler. The data will be sorted first. "
             "If `simplify` is true (default) then duplicates will be eliminated "
             "and only the newest version of each object kept. If `idx` is given "
             "a node location cache with the given type will be created and "
             "applied when creating the ways. Note that a diff file normally does "
             "not contain all node locations to reconstruct changed ways. If the "
             "full way geometries are needed, create a persistent node location "
             "cache during initial import of the area and reuse it when processing "
             "diffs. After the data "
             "has been applied the buffer of the MergeInputReader is empty and "
             "new data can be added for the next round of application.")
        .def("apply_to_reader", &MergeInputReader::apply_to_reader,
             py::arg("reader"), py::arg("writer"), py::arg("with_history")=false,
             "Apply the collected data to data from the given `reader` and write "
             "the result to `writer`. This function can be used to merge the diff "
             "data together with other OSM data (for example when updating a "
             "planet file. If `with_history` is true, then the collected data will "
             "be applied verbatim without removing duplicates. This is important "
             "when using OSM history files as input.")
        .def("add_file", &MergeInputReader::add_file,
             py::arg("file"),
             "Add data from a file to the internal cache. The file type will be "
             "determined from the file extension.")
        .def("add_buffer", &MergeInputReader::add_buffer,
             py::arg("buffer"), py::arg("format"),
             "Add data from a byte buffer. The format of the input data must "
             "be given in the `format` argument as a string. The data will be "
             "copied into internal buffers, so that the input buffer can be "
             "safely discarded after the function has been called.")
    ;
};
