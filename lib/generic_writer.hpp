#ifndef PYOSMIUM_GENERIC_WRITER_HPP
#define PYOSMIUM_GENERIC_WRITER_HPP


#include <osmium/osm.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/io/writer.hpp>
#include <osmium/memory/buffer.hpp>
#include <osmium/builder/osm_object_builder.hpp>
#include <boost/python.hpp>

class SimpleWriterWrap {

    enum { BUFFER_WRAP = 4096 };

public:
    SimpleWriterWrap(const char* filename, size_t bufsz=4096*1024)
    : writer(filename),
      buffer(bufsz < 2*BUFFER_WRAP ? 2*BUFFER_WRAP : bufsz, osmium::memory::Buffer::auto_grow::yes)
    {}

    virtual ~SimpleWriterWrap()
    {
        close();
    }

    void add_osmium_object(const osmium::OSMObject& o) {
        buffer.add_item(o);
        flush_buffer();
    }

    void add_node(boost::python::object o) {
        boost::python::extract<osmium::Node&> node(o);
        if (node.check()) {
            buffer.add_item(node());
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

    void add_way(const boost::python::object& o) {
        boost::python::extract<osmium::Way&> way(o);
        if (way.check()) {
            buffer.add_item(way());
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

    void add_relation(boost::python::object o) {
        boost::python::extract<osmium::Relation&> rel(o);
        if (rel.check()) {
            buffer.add_item(rel());
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

    void close() {
        if (buffer) {
            writer(std::move(buffer));
            writer.close();
            buffer = osmium::memory::Buffer();
        }
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
            boost::python::extract<osmium::Timestamp> ots(ts);
            if (ots.check()) {
                t.set_timestamp(ots());
            } else {
                if (hasattr(ts, "timestamp")) {
                    double epoch = boost::python::extract<double>(ts.attr("timestamp")());
                    t.set_timestamp(osmium::Timestamp(uint32_t(epoch)));
                } else
                {
                    // XXX terribly inefficient because of the double string conversion
                    //     but the only painless method for converting a datetime
                    //     in python < 3.3.
                    if (hasattr(ts, "strftime"))
                        ts = ts.attr("strftime")("%Y-%m-%dT%H:%M:%SZ");

                    t.set_timestamp(osmium::Timestamp(boost::python::extract<const char *>(ts)));
                }
            }
        }
    }

    template <typename T>
    void set_common_attributes(const boost::python::object& o, T& builder) {
        set_object_attributes(o, builder.object());

        if (hasattr(o, "user")) {
            auto s = boost::python::extract<const char *>(o.attr("user"));
            builder.set_user(s);
        }
    }

    template <typename T>
    void set_taglist(const boost::python::object& o, T& obuilder) {

        // original taglist
        boost::python::extract<osmium::TagList&> otl(o);
        if (otl.check()) {
            if (otl().size() > 0)
                obuilder.add_item(otl());
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
#if PY_VERSION_HEX < 0x03000000
                auto tag = iter.attr("next")();
#else
                auto tag = iter.attr("__next__")();
#endif
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
        // original nodelist
        boost::python::extract<osmium::NodeRefList&> onl(o);
        if (onl.check()) {
            if (onl().size() > 0)
                builder->add_item(onl());
            return;
        }

        auto len = boost::python::len(o);
        if (len == 0)
            return;

        osmium::builder::WayNodeListBuilder wnl_builder(buffer, builder);

        for (int i = 0; i < len; ++i) {
            boost::python::extract<osmium::NodeRef> ref(o[i]);
            if (ref.check())
                wnl_builder.add_node_ref(ref());
            else
                wnl_builder.add_node_ref(boost::python::extract<osmium::object_id_type>(o[i]));
        }
    }

    void set_memberlist(const boost::python::object& o,
                        osmium::builder::RelationBuilder *builder) {
        // original memberlist
        boost::python::extract<osmium::RelationMemberList&> oml(o);
        if (oml.check()) {
            if (oml().size() > 0)
                builder->add_item(oml());
            return;
        }

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

        if (buffer.committed() > buffer.capacity() - BUFFER_WRAP) {
            osmium::memory::Buffer new_buffer(buffer.capacity(), osmium::memory::Buffer::auto_grow::yes);
            using std::swap;
            swap(buffer, new_buffer);
            writer(std::move(new_buffer));
        }
    }

    osmium::io::Writer writer;
    osmium::memory::Buffer buffer;
};

#endif // PYOSMIUM_GENERIC_WRITER_HPP
