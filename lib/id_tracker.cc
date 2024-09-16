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
#include <osmium/io/any_input.hpp>
#include <osmium/index/nwr_array.hpp>
#include <osmium/index/id_set.hpp>

#include "base_filter.h"
#include "osmium_module.h"

#include <filesystem>

namespace py = pybind11;

namespace {

using IdType = osmium::unsigned_object_id_type;
using IdSet = osmium::index::IdSetDense<IdType>;

class IdTracker
{
public:
    void add_references(py::object const &obj)
    {
        if (py::hasattr(obj, "nodes")) {
            auto const nlist = py::getattr(obj, "nodes");
            for (auto const ref : nlist) {
                auto const attr = py::getattr(ref, "ref", py::none());
                m_ids.nodes().set(attr.is_none() ? ref.cast<IdType>()
                                                 : attr.cast<IdType>());
            }
        } else if (py::hasattr(obj, "members")) {
            auto const mlist = py::getattr(obj, "members");
            for (auto const member: mlist) {
                std::string mtype;
                IdType id;
                if (py::isinstance<py::tuple>(member)) {
                    auto const t = member.cast<py::tuple>();
                    mtype = t[0].cast<std::string>();
                    id = t[1].cast<IdType>();
                } else {
                    mtype = member.attr("type").cast<std::string>();
                    id = member.attr("ref").cast<IdType>();
                }
                // ignore unknown types
                if (mtype.length() == 1
                    && (mtype.front() == 'n' || mtype.front() == 'w'
                        || mtype.front() == 'r')) {
                    m_ids(osmium::char_to_item_type(mtype.front())).set(id);
                }
            }
        }
    }


    bool contains_any_references(py::object const &obj) const
    {
        if (py::hasattr(obj, "nodes")) {
            auto const nlist = py::getattr(obj, "nodes");
            for (auto const ref : nlist) {
                auto const attr = py::getattr(ref, "ref", py::none());
                if (m_ids.nodes().get(attr.is_none() ? ref.cast<IdType>()
                                                     : attr.cast<IdType>())) {
                    return true;
                }
            }
            return false;
        }

        if (py::hasattr(obj, "members")) {
            auto const mlist = py::getattr(obj, "members");
            for (auto const member: mlist) {
                std::string mtype;
                IdType id;
                if (py::isinstance<py::tuple>(member)) {
                    auto const t = member.cast<py::tuple>();
                    mtype = t[0].cast<std::string>();
                    id = t[1].cast<IdType>();
                } else {
                    mtype = member.attr("type").cast<std::string>();
                    id = member.attr("ref").cast<IdType>();
                }
                if (m_ids(osmium::char_to_item_type(mtype.front())).get(id)) {
                    return true;
                }
            }
        }

        return false;
    }


    void complete_backward_references(osmium::io::File file, int relation_depth)
    {
        // first pass: relations
        while (relation_depth > 0 && !m_ids.relations().empty()) {
            bool need_recurse = false;
            osmium::io::Reader rd{file, osmium::osm_entity_bits::relation};
            while (auto const buffer = rd.read()) {
                for (auto const &rel: buffer.select<osmium::Relation>()) {
                    if (m_ids.relations().get(rel.id())) {
                        for (auto const &member: rel.members()) {
                            if (member.type() == osmium::item_type::relation
                                && !m_ids.relations().get(member.ref())) {
                                need_recurse = true;
                            }
                            m_ids(member.type()).set(member.ref());
                        }
                    }
                }
            }
            if (!need_recurse) {
                break;
            }
            --relation_depth;
        }

        // second pass: ways
        if (!m_ids.ways().empty()) {
            osmium::io::Reader rd{file, osmium::osm_entity_bits::way};
            while (auto const buffer = rd.read()) {
                for (auto const &way: buffer.select<osmium::Way>()) {
                    if (m_ids.ways().get(way.id())) {
                        for (auto const &nd: way.nodes()) {
                            m_ids.nodes().set(nd.ref());
                        }
                    }
                }
            }
        }
    }


    void complete_forward_references(osmium::io::File file, int relation_depth)
    {
        // standard pass: find directly referenced ways and relations
        {
            auto entities = osmium::osm_entity_bits::way;
            if (relation_depth >= 0) {
                entities |= osmium::osm_entity_bits::relation;
            }
            osmium::io::Reader rd{file, entities};
            while (auto const buffer = rd.read()) {
                for (auto const &object: buffer.select<osmium::OSMObject>()) {
                    if (object.type() == osmium::item_type::way) {
                        const auto& way = static_cast<const osmium::Way&>(object);
                        for (const auto& nr : way.nodes()) {
                            if (m_ids(osmium::item_type::node).get(nr.positive_ref())) {
                                m_ids(osmium::item_type::way).set(way.id());
                                break;
                            }
                        }
                    } else if (object.type() == osmium::item_type::relation) {
                        const auto& relation = static_cast<const osmium::Relation&>(object);
                        for (const auto& member : relation.members()) {
                            if (member.type() != osmium::item_type::relation) {
                                if (m_ids(member.type()).get(member.positive_ref())) {
                                    m_ids(osmium::item_type::relation).set(relation.id());
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }

        // recursive passes: find additional referenced relations
        while (relation_depth > 0 && !m_ids.relations().empty()) {
            bool need_recurse = false;
            osmium::io::Reader rd{file, osmium::osm_entity_bits::relation};
            while (auto const buffer = rd.read()) {
                for (auto const &rel: buffer.select<osmium::Relation>()) {
                    if (!m_ids.relations().get(rel.id())) {
                        for (auto const &member: rel.members()) {
                            if (member.type() == osmium::item_type::relation
                                && m_ids.relations().get(member.ref())) {
                                need_recurse = true;
                                m_ids(member.type()).set(rel.id());
                                break;
                            }
                        }
                    }
                }
            }
            if (!need_recurse) {
                break;
            }
            --relation_depth;
        }

    }


    IdSet const &node_ids() const { return m_ids.nodes(); }
    IdSet const &way_ids() const { return m_ids.ways(); }
    IdSet const &relation_ids() const { return m_ids.relations(); }

    IdSet const &ids(osmium::item_type itype) const { return m_ids(itype); }

    IdSet &node_ids() { return m_ids.nodes(); }
    IdSet &way_ids() { return m_ids.ways(); }
    IdSet &relation_ids() { return m_ids.relations(); }

private:
    osmium::nwr_array<IdSet> m_ids;
};


class IdTrackerFilter : public pyosmium::BaseFilter
{
public:
    IdTrackerFilter(IdTracker const &tracker)
    : m_tracker(tracker)
    {
        m_enabled_for = osmium::osm_entity_bits::nwr;
    }

protected:
    bool filter_node(pyosmium::PyOSMNode &o) override {
        return !m_tracker.node_ids().get(o.get()->id());
    }

    bool filter_way(pyosmium::PyOSMWay &o) override {
        return !m_tracker.way_ids().get(o.get()->id());
    }

    bool filter_relation(pyosmium::PyOSMRelation &o) override {
        return !m_tracker.relation_ids().get(o.get()->id());
    }

private:
    IdTracker const &m_tracker;
};


class IdContainsFilter : public pyosmium::BaseFilter
{
public:
    IdContainsFilter(IdTracker const &tracker)
    : m_tracker(tracker)
    {
        m_enabled_for = osmium::osm_entity_bits::way | osmium::osm_entity_bits::relation;
    }

protected:
    bool filter_way(pyosmium::PyOSMWay &o) override {
        for (auto const &node : o.get()->nodes()) {
            if (m_tracker.node_ids().get(node.ref())) {
                return false;
            }
        }
        return true;
    }

    bool filter_relation(pyosmium::PyOSMRelation &o) override {
        for (auto const &member: o.get()->members()) {
            if (m_tracker.ids(member.type()).get(member.ref())) {
                return false;
            }
        }
        return true;
    }


private:
    IdTracker const &m_tracker;
};

} // namespace

namespace pyosmium {

void init_id_tracker(pybind11::module &m)
{
    py::class_<IdTrackerFilter, BaseFilter, BaseHandler>(m, "IdTrackerIdFilter")
    ;
    py::class_<IdContainsFilter, BaseFilter, BaseHandler>(m, "IdTrackerContainsFilter")
    ;

    py::class_<IdTracker>(m, "IdTracker")
        .def(py::init<>())
        .def("add_node", [](IdTracker &self, IdType id) { self.node_ids().set(id); })
        .def("add_way", [](IdTracker &self, IdType id) { self.way_ids().set(id); })
        .def("add_relation", [](IdTracker &self, IdType id) { self.relation_ids().set(id); })
        .def("add_references", &IdTracker::add_references)
        .def("contains_any_references", &IdTracker::contains_any_references)
        .def("complete_backward_references", &IdTracker::complete_backward_references,
             py::arg("fname"), py::arg("relation_depth") = 0)
        .def("complete_backward_references",
             [](IdTracker &self, char const *fname, int relation_depth) {
                self.complete_backward_references(osmium::io::File{fname}, relation_depth);
             },
             py::arg("fname"), py::arg("relation_depth") = 0)
        .def("complete_backward_references",
             [](IdTracker &self, std::filesystem::path const &fname, int relation_depth) {
                self.complete_backward_references(osmium::io::File{fname.string()}, relation_depth);
             },
             py::arg("fname"), py::arg("relation_depth") = 0)
        .def("complete_forward_references", &IdTracker::complete_forward_references,
             py::arg("fname"), py::arg("relation_depth") = 0)
        .def("complete_forward_references",
             [](IdTracker &self, char const *fname, int relation_depth) {
                self.complete_forward_references(osmium::io::File{fname}, relation_depth);
             },
             py::arg("fname"), py::arg("relation_depth") = 0)
        .def("complete_forward_references",
             [](IdTracker &self, std::filesystem::path const &fname, int relation_depth) {
                self.complete_forward_references(osmium::io::File{fname.string()}, relation_depth);
             },
             py::arg("fname"), py::arg("relation_depth") = 0)
        .def("id_filter",
             [](IdTracker const &self) { return new IdTrackerFilter(self); },
             py::keep_alive<0, 1>())
        .def("contains_filter",
             [](IdTracker const &self) { return new IdContainsFilter(self); },
             py::keep_alive<0, 1>())
        .def("node_ids", (IdSet& (IdTracker::*)()) &IdTracker::node_ids,
             py::return_value_policy::reference_internal)
        .def("way_ids", (IdSet& (IdTracker::*)()) &IdTracker::way_ids,
             py::return_value_policy::reference_internal)
        .def("relation_ids", (IdSet& (IdTracker::*)()) &IdTracker::relation_ids,
             py::return_value_policy::reference_internal)
    ;
}

} // namespace
