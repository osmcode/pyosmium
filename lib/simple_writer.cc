#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/io/writer.hpp>
#include <osmium/memory/buffer.hpp>
#include <osmium/builder/osm_object_builder.hpp>

#include "cast.h"

namespace py = pybind11;

namespace {

class SimpleWriter
{
    enum { BUFFER_WRAP = 4096 };

public:
    SimpleWriter(const char* filename, size_t bufsz=4096*1024)
    : writer(filename),
      buffer(bufsz < 2 * BUFFER_WRAP ? 2 * BUFFER_WRAP : bufsz,
             osmium::memory::Buffer::auto_grow::yes),
      buffer_size(buffer.capacity()) // same rounding to BUFFER_WRAP
    {}

    virtual ~SimpleWriter()
    { close(); }

    void add_osmium_object(const osmium::OSMObject& o)
    {
        buffer.add_item(o);
        flush_buffer();
    }

    void add_node(py::object o)
    {
        if (py::isinstance<osmium::Node>(o)) {
            buffer.add_item(o.cast<osmium::Node &>());
        } else {
            osmium::builder::NodeBuilder builder(buffer);

            if (hasattr(o, "location")) {
                osmium::Node& n = builder.object();
                n.set_location(get_location(o.attr("location")));
            }

            set_common_attributes(o, builder);

            if (hasattr(o, "tags"))
                set_taglist(o.attr("tags"), builder);
        }

        flush_buffer();
    }

    void add_way(py::object o)
    {
        if (py::isinstance<osmium::Way>(o)) {
            buffer.add_item(o.cast<osmium::Way &>());
        } else {
            osmium::builder::WayBuilder builder(buffer);

            set_common_attributes(o, builder);

            if (hasattr(o, "nodes"))
                set_nodelist(o.attr("nodes"), &builder);

            if (hasattr(o, "tags"))
                set_taglist(o.attr("tags"), builder);
        }

        flush_buffer();
    }

    void add_relation(py::object o)
    {
        if (py::isinstance<osmium::Relation>(o)) {
            buffer.add_item(o.cast<osmium::Relation &>());
        } else {
            osmium::builder::RelationBuilder builder(buffer);

            set_common_attributes(o, builder);

            if (hasattr(o, "members"))
                set_memberlist(o.attr("members"), &builder);

            if (hasattr(o, "tags"))
                set_taglist(o.attr("tags"), builder);
        }

        flush_buffer();
    }

    void close()
    {
        if (buffer) {
            writer(std::move(buffer));
            writer.close();
            buffer = osmium::memory::Buffer();
        }
    }

private:
    void set_object_attributes(py::object o, osmium::OSMObject& t)
    {
        if (hasattr(o, "id"))
            t.set_id(o.attr("id").cast<osmium::object_id_type>());
        if (hasattr(o, "visible"))
            t.set_visible(o.attr("visible").cast<bool>());
        if (hasattr(o, "version"))
            t.set_version(o.attr("version").cast<osmium::object_version_type>());
        if (hasattr(o, "changeset"))
            t.set_changeset(o.attr("changeset").cast<osmium::changeset_id_type>());
        if (hasattr(o, "uid"))
            t.set_uid_from_signed(o.attr("uid").cast<osmium::signed_user_id_type>());
        if (hasattr(o, "timestamp")) {
            t.set_timestamp(o.attr("timestamp").cast<osmium::Timestamp>());
        }
    }

    template <typename T>
    void set_common_attributes(py::object o, T& builder)
    {
        set_object_attributes(o, builder.object());

        if (hasattr(o, "user")) {
            builder.set_user(o.attr("user").cast<std::string>());
        }
    }

    template <typename T>
    void set_taglist(py::object o, T& obuilder)
    {
        // original taglist
        if (py::isinstance<osmium::TagList>(o)) {
            auto &otl = o.cast<osmium::TagList&>();
            if (otl.size() > 0)
                obuilder.add_item(otl);
            return;
        }

        // dict
        if (py::isinstance<py::dict>(o)) {
            if (py::len(o) == 0)
                return;

            osmium::builder::TagListBuilder builder(buffer, &obuilder);
            auto dict = o.cast<py::dict>();
            for (auto k : o) {
                builder.add_tag(k.cast<std::string>(),
                                dict[k].cast<std::string>());
            }
            return;
        }

        // else must be an iterable
        auto it = o.cast<py::iterable>();

        if (py::len(o) == 0)
            return;

        osmium::builder::TagListBuilder builder(buffer, &obuilder);
        for (auto item : it) {
            if (py::isinstance<osmium::Tag>(item)) {
                builder.add_tag(item.cast<osmium::Tag &>());
            } else {
                auto tag = item.cast<py::tuple>();
                builder.add_tag(tag[0].cast<std::string>(),
                                tag[1].cast<std::string>());
            }
        }
    }

    void set_nodelist(py::object o, osmium::builder::WayBuilder *builder)
    {
        // original nodelist
        if (py::isinstance<osmium::NodeRefList>(o)) {
            auto &onl = o.cast<osmium::NodeRefList &>();
            if (onl.size() > 0)
                builder->add_item(onl);
            return;
        }

        // accept an iterable of IDs otherwise
        auto it = o.cast<py::iterable>();

        if (py::len(o) == 0)
            return;

        osmium::builder::WayNodeListBuilder wnl_builder(buffer, builder);

        for (auto ref : it) {
            if (py::isinstance<osmium::NodeRef>(ref))
                wnl_builder.add_node_ref(ref.cast<osmium::NodeRef>());
            else
                wnl_builder.add_node_ref(ref.cast<osmium::object_id_type>());
        }
    }

    void set_memberlist(py::object o, osmium::builder::RelationBuilder *builder)
    {
        // original memberlist
        if (py::isinstance<osmium::RelationMemberList>(o)) {
            auto &oml = o.cast<osmium::RelationMemberList &>();
            if (oml.size() > 0)
                builder->add_item(oml);
            return;
        }

        // accept an iterable of (type, id, role) otherwise
        auto it = o.cast<py::iterable>();

        if (py::len(o) == 0)
            return;

        osmium::builder::RelationMemberListBuilder rml_builder(buffer, builder);

        for (auto m: it) {
            auto member = m.cast<py::tuple>();
            auto type = member[0].cast<std::string>();
            auto id = member[1].cast<osmium::object_id_type>();
            auto role = member[2].cast<std::string>();
            rml_builder.add_member(osmium::char_to_item_type(type[0]), id, role.c_str());
        }
    }

    osmium::Location get_location(py::object o)
    {
        if (py::isinstance<osmium::Location>(o)) {
            return o.cast<osmium::Location>();
        }

        // default is a tuple with two doubles
        auto l = o.cast<py::tuple>();
        return osmium::Location(l[0].cast<double>(), l[1].cast<double>());
    }

    void flush_buffer()
    {
        buffer.commit();

        if (buffer.committed() > buffer_size - BUFFER_WRAP) {
            osmium::memory::Buffer new_buffer(buffer_size, osmium::memory::Buffer::auto_grow::yes);
            using std::swap;
            swap(buffer, new_buffer);
            writer(std::move(new_buffer));
        }
    }

    bool hasattr(py::object o, char const *attr) const
    { return py::hasattr(o, attr) && !o.attr(attr).is_none(); }

    osmium::io::Writer writer;
    osmium::memory::Buffer buffer;
    size_t buffer_size;
};

}

void init_simple_writer(pybind11::module &m)
{
    py::class_<SimpleWriter>(m, "SimpleWriter",
        "The most generic class to write osmium objects into a file. The writer "
        "takes a file name as its mandatory parameter. The file must not yet "
        "exist. The file type to output is determined from the file extension. "
        "The second (optional) parameter is the buffer size. osmium caches the "
        "output data in an internal memory buffer before writing it on disk. This "
        "parameter allows changing the default buffer size of 4MB. Larger buffers "
        "are normally better but you should be aware that there are normally multiple "
        "buffers in use during the write process.")
        .def(py::init<const char*, unsigned long>())
        .def(py::init<const char*>())
        .def("add_node", &SimpleWriter::add_node, py::arg("node"),
             "Add a new node to the file. The node may be an ``osmium.osm.Node`` object, "
             "an ``osmium.osm.mutable.Node`` object or any other Python object that "
             "implements the same attributes.")
        .def("add_way", &SimpleWriter::add_way, py::arg("way"),
             "Add a new way to the file. The way may be an ``osmium.osm.Way`` object, "
             "an ``osmium.osm.mutable.Way`` object or any other Python object that "
             "implements the same attributes.")
        .def("add_relation", &SimpleWriter::add_relation, py::arg("relation"),
             "Add a new relation to the file. The relation may be an "
             "``osmium.osm.Relation`` object, an ``osmium.osm.mutable.Relation`` "
             "object or any other Python object that implements the same attributes.")
        .def("close", &SimpleWriter::close,
             "Flush the remaining buffers and close the writer. While it is not "
             "strictly necessary to call this function explicitly, it is still "
             "strongly recommended to close the writer as soon as possible, so "
             "that the buffer memory can be freed.")
    ;
}
