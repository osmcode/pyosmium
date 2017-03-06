#ifndef PYOSMIUM_MERGED_INPUT_HPP
#define PYOSMIUM_MERGED_INPUT_HPP

#include <vector>

#include <boost/function_output_iterator.hpp>

#include <osmium/osm/object_comparisons.hpp>
#include <osmium/io/any_input.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/io/output_iterator.hpp>
#include <osmium/handler.hpp>
#include <osmium/object_pointer_collection.hpp>
#include <osmium/visitor.hpp>

#include <boost/python.hpp>

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

} // anonymous namespace


namespace pyosmium {

class MergeInputReader {
public:
    void apply(BaseHandler& handler, bool simplify = true) {
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

    void apply_to_reader(osmium::io::Reader &reader, osmium::io::Writer &writer,
                         bool with_history = true) {
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

    size_t add_file(const std::string &filename) {
        return internal_add(osmium::io::File(filename));
    }

    size_t add_buffer(const boost::python::object &buf,
                      const boost::python::str &format) {
        Py_buffer pybuf;
        PyObject_GetBuffer(buf.ptr(), &pybuf, PyBUF_C_CONTIGUOUS);
        size_t len = (size_t) pybuf.len;
        const char *cbuf = reinterpret_cast<const char *>(pybuf.buf);
        const char *cfmt = boost::python::extract<const char *>(format);

        return internal_add(osmium::io::File(cbuf, len, cfmt));
    }

private:
    size_t internal_add(osmium::io::File change_file) {
        size_t sz = 0;
        osmium::io::Reader reader(change_file, osmium::osm_entity_bits::object);
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

#endif /* PYOSMIUM_MERGED_INPUT_HPP */
