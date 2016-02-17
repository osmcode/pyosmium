#ifndef PYOSMIUM_MERGED_INPUT_HPP
#define PYOSMIUM_MERGED_INPUT_HPP

#include <vector>

#include <osmium/osm/object_comparisons.hpp>
#include <osmium/io/any_input.hpp>
#include <osmium/handler.hpp>
#include <osmium/object_pointer_collection.hpp>
#include <osmium/visitor.hpp>

#include <boost/python.hpp>

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
