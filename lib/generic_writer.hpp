#ifndef PYOSMIUM_GENERIC_WRITER_HPP
#define PYOSMIUM_GENERIC_WRITER_HPP

#include <boost/python.hpp>

#include <osmium/osm.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/io/writer.hpp>
#include <osmium/memory/buffer.hpp>
#include <osmium/builder/osm_object_builder.hpp>

class SimpleWriterWrap {

public:
    SimpleWriterWrap(const char* filename)
    : writer(filename),
      buffer(1024*1024, osmium::memory::Buffer::auto_grow::yes)
    {}

    void add_osmium_object(const osmium::OSMObject& o) {
        buffer.add_item(o);
        flush_buffer();
    }

    void add_node(boost::python::object o) {
        osmium::builder::NodeBuilder builder(buffer);
        osmium::Node& node = builder.object();

        if (hasattr(o, "location"))
            node.set_location(get_location(o.attr("location")));

        set_common_attributes(o, builder);

        if (hasattr(o, "tags"))
            set_taglist(o.attr("tags"), builder);

        flush_buffer();
    }

    void add_way(boost::python::object o) {
        osmium::builder::WayBuilder builder(buffer);

        set_common_attributes(o, builder);

        if (hasattr(o, "nodes"))
            set_nodelist(o.attr("nodes"), &builder);

        if (hasattr(o, "tags"))
            set_taglist(o.attr("tags"), builder);

        flush_buffer();
    }

    void add_relation(boost::python::object o) {
        osmium::builder::RelationBuilder builder(buffer);

        set_common_attributes(o, builder);

        if (hasattr(o, "members"))
            set_memberlist(o.attr("members"), &builder);

        if (hasattr(o, "tags"))
            set_taglist(o.attr("tags"), builder);

        flush_buffer();
    }

    void close() {
        writer(std::move(buffer));
        writer.close();
    }

private:
    void set_object_attributes(const boost::python::object& o, osmium::OSMObject& t) {
        if (hasattr(o, "id"))
            t.set_id(boost::python::extract<osmium::object_id_type>(o.attr("id")));
        if (hasattr(o, "visible"))
            t.set_visible(boost::python::extract<bool>(o.attr("visible")));
        if (hasattr(o, "version"))
            t.set_version(boost::python::extract<osmium::object_version_type>(o.attr("version")));
        if (hasattr(o, "changeset"))
            t.set_changeset(boost::python::extract<osmium::changeset_id_type>(o.attr("changeset")));
        if (hasattr(o, "uid"))
            t.set_uid_from_signed(boost::python::extract<osmium::signed_user_id_type>(o.attr("uid")));
        if (hasattr(o, "timestamp")) {
            boost::python::object ts = o.attr("timestamp");
            // XXX terribly inefficient because of the double string conversion
            if (hasattr(ts, "strftime"))
                ts = ts.attr("strftime")("%Y-%m-%dT%H:%M:%SZ");

            t.set_timestamp(osmium::Timestamp(boost::python::extract<const char *>(ts)));
        }
    }

    template <typename T>
    void set_common_attributes(const boost::python::object& o, T& builder) {
        set_object_attributes(o, builder.object());

        if (hasattr(o, "user")) {
            auto s = boost::python::extract<const char *>(o.attr("user"));
            builder.add_user(s);
        } else {
            builder.add_user("", 0);
        }
    }

    template <typename T>
    void set_taglist(const boost::python::object& o, T& obuilder) {

        // original taglist
        boost::python::extract<osmium::TagList&> otl(o);
        if (otl.check()) {
            if (otl().size() == 0)
                return;

            osmium::builder::TagListBuilder builder(buffer, &obuilder);
            for (const auto& tag : otl()) {
                builder.add_tag(tag);
            }
            return;
        }

        // dict
        boost::python::extract<boost::python::dict> tagdict(o);
        if (tagdict.check()) {
            auto items = tagdict().items();
            auto len = boost::python::len(items);
            if (len == 0)
                return;

            osmium::builder::TagListBuilder builder(buffer, &obuilder);
            auto iter = items.attr("__iter__")();
            for (int i = 0; i < len; ++i) {
                auto tag = iter.attr("__next__")();
                builder.add_tag(boost::python::extract<const char *>(tag[0]),
                                boost::python::extract<const char *>(tag[1]));
            }
            return;
        }

        // any other iterable
        auto l = boost::python::len(o);
        if (l == 0)
            return;

        osmium::builder::TagListBuilder builder(buffer, &obuilder);
        for (int i = 0; i < l; ++i) {
            auto tag = o[i];

            boost::python::extract<osmium::Tag> ot(tag);
            if (ot.check()) {
                builder.add_tag(ot);
            } else {
                builder.add_tag(boost::python::extract<const char *>(tag[0]),
                                boost::python::extract<const char *>(tag[1]));
            }
        }
    }

    void set_nodelist(const boost::python::object& o,
                      osmium::builder::WayBuilder *builder) {
        auto len = boost::python::len(o);
        if (len == 0)
            return;

        osmium::builder::WayNodeListBuilder wnl_builder(buffer, builder);

        for (int i = 0; i < len; ++i) {
            wnl_builder.add_node_ref(boost::python::extract<osmium::object_id_type>(o[i]));
        }
    }

    void set_memberlist(const boost::python::object& o,
                        osmium::builder::RelationBuilder *builder) {
        auto len = boost::python::len(o);
        if (len == 0)
            return;

        osmium::builder::RelationMemberListBuilder rml_builder(buffer, builder);

        for (int i = 0; i < len; ++i) {
            auto member = o[i];
            auto type = osmium::char_to_item_type(boost::python::extract<const char*>(member[0])()[0]);
            auto id = boost::python::extract<osmium::object_id_type>(member[1])();
            auto role = boost::python::extract<const char*>(member[2])();
            rml_builder.add_member(type, id, role);
        }
    }

    osmium::Location get_location(const boost::python::object& o) {
        boost::python::extract<osmium::Location> ol(o);
        if (ol.check())
            return ol;

        // default is a tuple with two floats
        return osmium::Location(boost::python::extract<float>(o[0]),
                                boost::python::extract<float>(o[1]));
    }

    bool hasattr(const boost::python::object& obj, char const *attr) {
        return PyObject_HasAttrString(obj.ptr(), attr)
                && (obj.attr(attr) != boost::python::object());
    }

    void flush_buffer() {
        buffer.commit();

        if (buffer.committed() > 900*1024) {
            osmium::memory::Buffer new_buffer(1024*1024, osmium::memory::Buffer::auto_grow::yes);
            using std::swap;
            swap(buffer, new_buffer);
            writer(std::move(new_buffer));
        }
    }

    osmium::io::Writer writer;
    osmium::memory::Buffer buffer;
};

#endif // PYOSMIUM_GENERIC_WRITER_HPP
