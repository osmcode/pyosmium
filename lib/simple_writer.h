#ifndef PYOSMIUM_SIMPLE_WRITER_HPP
#define PYOSMIUM_SIMPLE_WRITER_HPP

#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/io/writer.hpp>
#include <osmium/memory/buffer.hpp>
#include <osmium/builder/osm_object_builder.hpp>
#include <boost/python.hpp>

#include "cast.h"

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

    void add_node(pybind11::object o)
    {
        if (pybind11::isinstance<osmium::Node>(o)) {
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

    void add_way(pybind11::object o)
    {
        if (pybind11::isinstance<osmium::Way>(o)) {
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

    void add_relation(pybind11::object o)
    {
        if (pybind11::isinstance<osmium::Relation>(o)) {
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
    void set_object_attributes(pybind11::object o, osmium::OSMObject& t)
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
    void set_common_attributes(pybind11::object o, T& builder)
    {
        set_object_attributes(o, builder.object());

        if (hasattr(o, "user")) {
            builder.set_user(o.attr("user").cast<std::string>());
        }
    }

    template <typename T>
    void set_taglist(pybind11::object o, T& obuilder)
    {
        // original taglist
        if (pybind11::isinstance<osmium::TagList>(o)) {
            auto &otl = o.cast<osmium::TagList&>();
            if (otl.size() > 0)
                obuilder.add_item(otl);
            return;
        }

        // dict
        if (pybind11::isinstance<pybind11::dict>(o)) {
            if (pybind11::len(o) == 0)
                return;

            osmium::builder::TagListBuilder builder(buffer, &obuilder);
            for (auto item : o.cast<pybind11::dict>()) {
                builder.add_tag(item.first.cast<std::string>(),
                                item.second.cast<std::string>());
            }
            return;
        }

        // else must be an iterable other iterable
        auto it = o.cast<pybind11::iterable>();

        if (pybind11::len(o) == 0)
            return;

        osmium::builder::TagListBuilder builder(buffer, &obuilder);
        for (auto item : it) {
            if (pybind11::isinstance<osmium::Tag>(item)) {
                builder.add_tag(item.cast<osmium::Tag &>());
            } else {
                auto tag = item.cast<pybind11::tuple>();
                builder.add_tag(tag[0].cast<std::string>(),
                                tag[1].cast<std::string>());
            }
        }
    }

    void set_nodelist(pybind11::object o, osmium::builder::WayBuilder *builder)
    {
        // original nodelist
        if (pybind11::isinstance<osmium::NodeRefList>(o)) {
            auto &onl = o.cast<osmium::NodeRefList &>();
            if (onl.size() > 0)
                builder->add_item(onl);
            return;
        }

        // accept an iterable of IDs otherwise
        auto it = o.cast<pybind11::iterable>();

        if (pybind11::len(o) == 0)
            return;

        osmium::builder::WayNodeListBuilder wnl_builder(buffer, builder);

        for (auto ref : it) {
            if (pybind11::isinstance<osmium::NodeRef>(ref))
                wnl_builder.add_node_ref(ref.cast<osmium::NodeRef>());
            else
                wnl_builder.add_node_ref(ref.cast<osmium::object_id_type>());
        }
    }

    void set_memberlist(pybind11::object o, osmium::builder::RelationBuilder *builder)
    {
        // original memberlist
        if (pybind11::isinstance<osmium::RelationMemberList>(o)) {
            auto &oml = o.cast<osmium::RelationMemberList &>();
            if (oml.size() > 0)
                builder->add_item(oml);
            return;
        }

        // accept an iterable of (type, id, role) otherwise
        auto it = o.cast<pybind11::iterable>();

        if (pybind11::len(o) == 0)
            return;

        osmium::builder::RelationMemberListBuilder rml_builder(buffer, builder);

        for (auto m: it) {
            auto member = m.cast<pybind11::tuple>();
            auto type = member[0].cast<std::string>();
            auto id = member[1].cast<osmium::object_id_type>();
            auto role = member[2].cast<std::string>();
            rml_builder.add_member(osmium::char_to_item_type(type[0]), id, role.c_str());
        }
    }

    osmium::Location get_location(pybind11::object o)
    {
        if (pybind11::isinstance<osmium::Location>(o)) {
            return o.cast<osmium::Location>();
        }

        // default is a tuple with two floats
        auto l = o.cast<pybind11::tuple>();
        return osmium::Location(l[0].cast<float>(), l[1].cast<float>());
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

    bool hasattr(pybind11::object o, char const *attr) const
    { return pybind11::hasattr(o, attr) && !o.attr(attr).is_none(); }

    osmium::io::Writer writer;
    osmium::memory::Buffer buffer;
    size_t buffer_size;
};

#endif // PYOSMIUM_SIMPLE_WRITER_HPP
