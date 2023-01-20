/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2023 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/io/writer.hpp>
#include <osmium/io/header.hpp>
#include <osmium/memory/buffer.hpp>
#include <osmium/builder/osm_object_builder.hpp>

#include "cast.h"
#include "osm_base_objects.h"

namespace py = pybind11;

namespace {

class SimpleWriter
{
    enum { BUFFER_WRAP = 4096 };

public:
    SimpleWriter(const char* filename, size_t bufsz=4096*1024, osmium::io::Header header=osmium::io::Header())
    : writer(filename, header),
      buffer(bufsz < 2 * BUFFER_WRAP ? 2 * BUFFER_WRAP : bufsz,
             osmium::memory::Buffer::auto_grow::yes),
      buffer_size(buffer.capacity()) // same rounding to BUFFER_WRAP
    {}

    virtual ~SimpleWriter()
    { close(); }

    void add_node(py::object o)
    {
        if (!buffer) {
            throw std::runtime_error{"Writer already closed."};
        }

        buffer.rollback();

        auto const *inode = pyosmium::try_cast<COSMNode>(o);
        if (inode) {
            buffer.add_item(*inode->get());
        } else {
            osmium::builder::NodeBuilder builder(buffer);

            auto const location = py::getattr(o, "location", py::none());
            if (!location.is_none()) {
                osmium::Node& n = builder.object();
                n.set_location(get_location(location));
            }

            set_common_attributes(o, builder);
            set_taglist<COSMNode>(o, builder);
        }

        flush_buffer();
    }

    void add_way(py::object o)
    {
        if (!buffer) {
            throw std::runtime_error{"Writer already closed."};
        }

        buffer.rollback();

        auto const *iobj = pyosmium::try_cast<COSMWay>(o);
        if (iobj) {
            buffer.add_item(*iobj->get());
        } else {
            osmium::builder::WayBuilder builder(buffer);

            set_common_attributes(o, builder);
            set_nodelist(o, &builder);
            set_taglist<COSMWay>(o, builder);
        }

        flush_buffer();
    }

    void add_relation(py::object o)
    {
        if (!buffer) {
            throw std::runtime_error{"Writer already closed."};
        }

        buffer.rollback();

        auto const *iobj = pyosmium::try_cast<COSMRelation>(o);
        if (iobj) {
            buffer.add_item(*iobj->get());
        } else {
            osmium::builder::RelationBuilder builder(buffer);

            set_common_attributes(o, builder);
            set_memberlist(o, &builder);
            set_taglist<COSMRelation>(o, builder);
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
    void set_object_attributes(py::object const &o, osmium::OSMObject& t)
    {
        {
            auto const id = py::getattr(o, "id", py::none());
            if (!id.is_none())
                t.set_id(id.cast<osmium::object_id_type>());
        }
        {
            auto const attr = py::getattr(o, "visible", py::none());
            if (!attr.is_none())
                t.set_visible(attr.cast<bool>());
        }
        {
            auto const attr = py::getattr(o, "version", py::none());
            if (!attr.is_none())
                t.set_version(attr.cast<osmium::object_version_type>());
        }
        {
            auto const attr = py::getattr(o, "changeset", py::none());
            if (!attr.is_none())
                t.set_changeset(attr.cast<osmium::changeset_id_type>());
        }
        {
            auto const attr = py::getattr(o, "uid", py::none());
            if (!attr.is_none())
                t.set_uid_from_signed(attr.cast<osmium::signed_user_id_type>());
        }
        {
            auto const attr = py::getattr(o, "timestamp", py::none());
            if (!attr.is_none())
                t.set_timestamp(attr.cast<osmium::Timestamp>());
        }
    }

    template <typename T>
    void set_common_attributes(py::object const &o, T& builder)
    {
        set_object_attributes(o, builder.object());

        auto const attr = py::getattr(o, "user", py::none());
        if (!attr.is_none())
            builder.set_user(attr.cast<std::string>());
    }

    template <typename Base, typename T>
    void set_taglist(py::object const &container, T& obuilder)
    {
        auto const o = py::getattr(container, "tags", py::none());

        if (o.is_none()) {
            return;
        }

        // original taglist
        auto const &iobj = pyosmium::try_cast<Base>(o);
        if (iobj) {
            auto const &otl = iobj->get()->tags();
            if (otl.size() > 0)
                obuilder.add_item(otl);
            return;
        }

        if (py::len(o) == 0)
            return;

        // dict
        if (py::isinstance<py::dict>(o)) {
            osmium::builder::TagListBuilder builder(buffer, &obuilder);
            auto const dict = o.cast<py::dict>();
            for (auto const &k : dict) {
                builder.add_tag(k.first.cast<std::string>(),
                                k.second.cast<std::string>());
            }
            return;
        }

        // else must be an iterable
        osmium::builder::TagListBuilder builder(buffer, &obuilder);
        for (auto const item : o) {
            auto const tag = item.cast<py::tuple>();
            builder.add_tag(tag[0].cast<std::string>(),
                            tag[1].cast<std::string>());
        }
    }

    void set_nodelist(py::object const &container, osmium::builder::WayBuilder *builder)
    {
        auto const o = py::getattr(container, "nodes", py::none());

        if (o.is_none()) {
            return;
        }

        // original nodelist
        auto const *onl = pyosmium::try_cast_list<osmium::WayNodeList>(o);
        if (onl) {
            if (onl->size() > 0)
                builder->add_item(*onl);
            return;
        }

        // accept an iterable of IDs otherwise
        if (py::len(o) == 0)
            return;

        osmium::builder::WayNodeListBuilder wnl_builder(buffer, builder);

        for (auto const ref : o) {
            auto const attr = py::getattr(ref, "ref", py::none());
            if (!attr.is_none())
                wnl_builder.add_node_ref(attr.cast<osmium::object_id_type>());
            else
                wnl_builder.add_node_ref(ref.cast<osmium::object_id_type>());
        }
    }

    void set_memberlist(py::object const &container, osmium::builder::RelationBuilder *builder)
    {
        auto const o = py::getattr(container, "members", py::none());

        if (o.is_none()) {
            return;
        }

        // original memberlist
        auto const &iobj = pyosmium::try_cast<COSMRelation>(o);
        if (iobj) {
            auto const &oml = iobj->get()->members();
            if (oml.size() > 0)
                builder->add_item(oml);
            return;
        }

        // accept an iterable of (type, id, role) otherwise
        if (py::len(o) == 0)
            return;

        osmium::builder::RelationMemberListBuilder rml_builder(buffer, builder);

        for (auto const m: o) {
            if (py::isinstance<py::tuple>(m)) {
                auto const member = m.cast<py::tuple>();
                auto const type = member[0].cast<std::string>();
                auto const id = member[1].cast<osmium::object_id_type>();
                auto const role = member[2].cast<std::string>();
                rml_builder.add_member(osmium::char_to_item_type(type[0]), id, role.c_str());
            } else {
                auto const type = m.attr("type").cast<std::string>();
                auto const id = m.attr("ref").cast<osmium::object_id_type>();
                auto const role = m.attr("role").cast<std::string>();
                rml_builder.add_member(osmium::char_to_item_type(type[0]), id, role.c_str());
            }
        }
    }

    osmium::Location get_location(py::object const &o) const
    {
        if (py::isinstance<osmium::Location>(o)) {
            return o.cast<osmium::Location>();
        }

        // default is a tuple with two doubles
        auto l = o.cast<py::tuple>();
        return osmium::Location{l[0].cast<double>(), l[1].cast<double>()};
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
        .def(py::init<const char*, unsigned long, osmium::io::Header>())
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
