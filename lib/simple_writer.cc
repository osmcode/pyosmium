/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>
#include <pybind11/stl/filesystem.h>

#include <osmium/osm.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/io/writer.hpp>
#include <osmium/io/header.hpp>
#include <osmium/memory/buffer.hpp>
#include <osmium/builder/osm_object_builder.hpp>

#include "cast.h"
#include "osm_base_objects.h"
#include "base_handler.h"

#include <filesystem>

namespace py = pybind11;

namespace {

class SimpleWriter : public pyosmium::BaseHandler
{
    enum { BUFFER_WRAP = 4096 };

public:
    SimpleWriter(const char* filename, size_t bufsz, osmium::io::Header const *header,
                 bool overwrite, const std::string &filetype)
    : writer(osmium::io::File(filename, filetype),
             header ? *header : osmium::io::Header(),
             overwrite ? osmium::io::overwrite::allow : osmium::io::overwrite::no),
      buffer(bufsz < 2 * BUFFER_WRAP ? 2 * BUFFER_WRAP : bufsz,
             osmium::memory::Buffer::auto_grow::yes),
      buffer_size(buffer.capacity()) // same rounding to BUFFER_WRAP
    {}

    SimpleWriter(osmium::io::File file, size_t bufsz, osmium::io::Header const *header,
                 bool overwrite)
    : writer(file, header ? *header : osmium::io::Header(),
             overwrite ? osmium::io::overwrite::allow : osmium::io::overwrite::no),
      buffer(bufsz < 2 * BUFFER_WRAP ? 2 * BUFFER_WRAP : bufsz,
             osmium::memory::Buffer::auto_grow::yes),
      buffer_size(buffer.capacity()) // same rounding to BUFFER_WRAP
    {}

    virtual ~SimpleWriter()
    { close(); }


    bool node(pyosmium::PyOSMNode &o) override
    {
        buffer.add_item(*(o.get()));
        flush_buffer();
        return false;
    }

    bool way(pyosmium::PyOSMWay &o) override
    {
        buffer.add_item(*(o.get()));
        flush_buffer();
        return false;
    }

    bool relation(pyosmium::PyOSMRelation &o) override
    {
        buffer.add_item(*(o.get()));
        flush_buffer();
        return false;
    }

    void flush() override
    {
        flush_buffer(true);
    }


    void add_node(py::object o)
    {
        if (!buffer) {
            throw std::runtime_error{"Writer already closed."};
        }

        buffer.rollback();

        auto const *inode = pyosmium::try_cast<pyosmium::COSMNode>(o);
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
            set_taglist<pyosmium::COSMNode>(o, builder);
        }

        flush_buffer();
    }

    void add_way(py::object o)
    {
        if (!buffer) {
            throw std::runtime_error{"Writer already closed."};
        }

        buffer.rollback();

        auto const *iobj = pyosmium::try_cast<pyosmium::COSMWay>(o);
        if (iobj) {
            buffer.add_item(*iobj->get());
        } else {
            osmium::builder::WayBuilder builder(buffer);

            set_common_attributes(o, builder);
            set_nodelist(o, &builder);
            set_taglist<pyosmium::COSMWay>(o, builder);
        }

        flush_buffer();
    }

    void add_relation(py::object o)
    {
        if (!buffer) {
            throw std::runtime_error{"Writer already closed."};
        }

        buffer.rollback();

        auto const *iobj = pyosmium::try_cast<pyosmium::COSMRelation>(o);
        if (iobj) {
            buffer.add_item(*iobj->get());
        } else {
            osmium::builder::RelationBuilder builder(buffer);

            set_common_attributes(o, builder);
            set_memberlist(o, &builder);
            set_taglist<pyosmium::COSMRelation>(o, builder);
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
        auto const &iobj = pyosmium::try_cast<pyosmium::COSMRelation>(o);
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

    void flush_buffer(bool force = false)
    {
        buffer.commit();

        if (force || buffer.committed() > buffer_size - BUFFER_WRAP) {
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

} // namespace

namespace pyosmium {

void init_simple_writer(pybind11::module &m)
{
    py::class_<SimpleWriter, BaseHandler>(m, "SimpleWriter")
        .def(py::init<const char*, unsigned long, osmium::io::Header const *, bool, const std::string&>(),
             py::arg("filename"), py::arg("bufsz") = 4096*1024,
             py::arg("header") = nullptr,
             py::arg("overwrite") = false,
             py::arg("filetype") = "")
        .def(py::init<>([] (std::filesystem::path const &file, unsigned long bufsz,
                            osmium::io::Header const *header, bool overwrite) {
                 return new SimpleWriter(file.string().c_str(), bufsz, header, overwrite, "");
             }),
             py::arg("filename"), py::arg("bufsz") = 4096*1024,
             py::arg("header") = nullptr,
             py::arg("overwrite") = false)
        .def(py::init<osmium::io::File, unsigned long, osmium::io::Header const *, bool>(),
             py::arg("filename"), py::arg("bufsz") = 4096*1024,
             py::arg("header") = nullptr,
             py::arg("overwrite") = false)
        .def("add_node", &SimpleWriter::add_node, py::arg("node"))
        .def("add_way", &SimpleWriter::add_way, py::arg("way"))
        .def("add_relation", &SimpleWriter::add_relation, py::arg("relation"))
        .def("add", [](SimpleWriter &self, py::object const &o) {
                           if (py::isinstance<pyosmium::COSMNode>(o) || py::hasattr(o, "location")) {
                               self.add_node(o);
                           } else if (py::isinstance<pyosmium::COSMWay>(o) || py::hasattr(o, "nodes")) {
                               self.add_way(o);
                           } else if (py::isinstance<pyosmium::COSMRelation>(o) || py::hasattr(o, "members")) {
                               self.add_relation(o);
                           } else {
                               throw py::type_error("Need node, way or relation object.");
                           }
                    })
        .def("close", &SimpleWriter::close)
        .def("__enter__", [](py::object const &self) { return self; })
        .def("__exit__", [](SimpleWriter &self, py::args args) { self.close(); })
    ;
}

} // namespace
