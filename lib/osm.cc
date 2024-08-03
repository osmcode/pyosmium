/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include <osmium/osm/entity_bits.hpp>

#include "cast.h"
#include "osm_base_objects.h"

namespace py = pybind11;

#if PYBIND11_VERSION_MINOR >= 11 || PYBIND11_VERSION_MAJOR > 2
/*
Work-around false positive added by pybind/pybind11@f701654 change:
ItemIterator/CollectionIterator ARE copy/move constructible, even if their template
parameter is not. Indeed, those iterators iterate over low-level memory representation
of the objects, without relying on their constructors.

For eg.
// static_assert(std::is_move_constructible<osmium::memory::CollectionIterator<osmium::RelationMember const>>::value);
// static_assert(!std::is_copy_constructible<osmium::RelationMember>::value);

The work-around relies on officially exposed pybind11::detail::is_copy_constructible/is_copy_constructible: 
https://github.com/pybind/pybind11/pull/4631
*/
namespace pybind11 {
namespace detail {
template <typename T>
struct is_copy_constructible<osmium::memory::CollectionIterator<T>>
    : std::true_type {};
template <typename T>
struct is_move_constructible<osmium::memory::CollectionIterator<T>>
    : std::true_type {};
template <typename T>
struct is_copy_constructible<osmium::memory::ItemIterator<T>>
    : std::true_type {};
template <typename T>
struct is_move_constructible<osmium::memory::ItemIterator<T>>
    : std::true_type {};
} // namespace detail
} // namespace pybind11
#endif

namespace {

using TagIterator = osmium::TagList::const_iterator;
using MemberIterator = osmium::RelationMemberList::const_iterator;

static py::object tag_iterator_next(TagIterator &it, TagIterator const &cend)
{
    if (it == cend)
        throw pybind11::stop_iteration();

    static auto const tag = pybind11::module_::import("osmium.osm.types").attr("Tag");
    auto const value = tag(it->key(), it->value());
    ++it;

    return value;
}


static py::object member_iterator_next(MemberIterator &it, MemberIterator const &cend)
{
    if (it == cend)
        throw pybind11::stop_iteration();

    static auto const obj = pybind11::module_::import("osmium.osm.types").attr("RelationMember");
    auto const value = obj(it->ref(), item_type_to_char(it->type()), it->role());
    ++it;

    return value;
}

using OuterRingIterator = osmium::memory::ItemIteratorRange<osmium::OuterRing const>::const_iterator;
using InnerRingIterator = osmium::memory::ItemIteratorRange<osmium::InnerRing const>::const_iterator;

template <typename T>
T const *ring_iterator_next(typename osmium::memory::ItemIteratorRange<T const>::const_iterator &it)
{
    if (!it)
        throw pybind11::stop_iteration();

    return &(*it++);
}

static pybind11::object get_node_item(osmium::NodeRefList const *list, Py_ssize_t idx)
{
    auto const sz = list->size();

    osmium::NodeRefList::size_type const iout =
        (idx >= 0 ? idx : (Py_ssize_t) sz + idx);

    if (iout >= sz || iout < 0) {
        throw pybind11::index_error("Bad index.");
    }

    auto const &node = (*list)[iout];

    static auto const node_ref_t = pybind11::module_::import("osmium.osm.types").attr("NodeRef");

    return node_ref_t(node.location(), node.ref());
}

template <typename T, typename P>
void make_node_list(py::module_ &m, char const *class_name)
{
    py::class_<T>(m, class_name)
        .def("size", [](T const *o, P const &parent)
            { parent.get(); return o->size(); })
        .def("get", [](T const *o, P const &parent, Py_ssize_t idx)
            { parent.get(); return get_node_item(o, idx); })
        .def("is_closed", [](T const *o, P const &parent)
            { parent.get(); return o->is_closed(); })
        .def("ends_have_same_location", [](T const *o, P const &parent)
            { parent.get(); return o->ends_have_same_location(); })
    ;
}


template <typename COSMObject>
py::class_<COSMObject> make_osm_object_class(py::module_ &m, char const *class_name)
{
    return py::class_<COSMObject>(m, class_name)
        .def("id", [](COSMObject const &o) { return o.get()->id(); })
        .def("deleted", [](COSMObject const &o) { return o.get()->deleted(); })
        .def("visible", [](COSMObject const &o) { return o.get()->visible(); })
        .def("version", [](COSMObject const &o) { return o.get()->version(); })
        .def("changeset", [](COSMObject const &o) { return o.get()->changeset(); })
        .def("uid", [](COSMObject const &o) { return o.get()->uid(); })
        .def("timestamp", [](COSMObject const &o) { return o.get()->timestamp(); })
        .def("user", [](COSMObject const &o) { return o.get()->user(); })
        .def("positive_id", [](COSMObject const &o) { return o.get()->positive_id(); })
        .def("user_is_anonymous", [](COSMObject const &o) { return o.get()->user_is_anonymous(); })
        .def("tags_size", [](COSMObject const &o) { return o.get()->tags().size(); })
        .def("tags_get_value_by_key", [](COSMObject const &o, char const *key, char const *def)
            { return o.get()->tags().get_value_by_key(key, def); })
        .def("tags_has_key", [](COSMObject const &o, char const *key)
            { return o.get()->tags().has_key(key); })
        .def("tags_begin", [](COSMObject const &o) { return o.get()->tags().cbegin(); })
        .def("tags_next", [](COSMObject const &o, TagIterator &it)
            { return tag_iterator_next(it, o.get()->tags().cend()); })
        .def("is_valid", &COSMObject::is_valid)
    ;
}

} // namespace


PYBIND11_MODULE(_osm, m) {
    py::enum_<osmium::osm_entity_bits::type>(m, "osm_entity_bits")
        .value("NOTHING", osmium::osm_entity_bits::nothing)
        .value("NODE", osmium::osm_entity_bits::node)
        .value("WAY", osmium::osm_entity_bits::way)
        .value("RELATION", osmium::osm_entity_bits::relation)
        .value("AREA", osmium::osm_entity_bits::area)
        .value("OBJECT", osmium::osm_entity_bits::object)
        .value("CHANGESET", osmium::osm_entity_bits::changeset)
        .value("ALL", osmium::osm_entity_bits::all)
        .export_values()
        .def("__or__", &osmium::osm_entity_bits::operator|)
        .def("__and__", &osmium::osm_entity_bits::operator&)
        .def("__invert__", &osmium::osm_entity_bits::operator~)
        .def("__bool__", [](osmium::osm_entity_bits::type e) { return e != osmium::osm_entity_bits::nothing; })
    ;


    py::class_<osmium::Box>(m, "Box",
        "A bounding box around a geographic area. It is defined by an "
        ":py:class:`osmium.osm.Location` for the bottem-left corner and an "
        "``osmium.osm.Location`` for the top-right corner. Those locations may "
        " be invalid in which case the box is considered invalid, too.")
        .def(py::init<double, double, double, double>())
        .def(py::init<osmium::Location, osmium::Location>())
        .def_property_readonly("bottom_left",
                               (osmium::Location& (osmium::Box::*)())
                                   &osmium::Box::bottom_left,
                               py::return_value_policy::reference_internal,
             "(read-only) Bottom-left corner of the bounding box.")
        .def_property_readonly("top_right",
                               (osmium::Location& (osmium::Box::*)())
                                   &osmium::Box::top_right,
                               py::return_value_policy::reference_internal,
             "(read-only) Top-right corner of the bounding box.")
        .def("extend",
             (osmium::Box& (osmium::Box::*)(osmium::Location const&))
                 &osmium::Box::extend,
             py::arg("location"),
             py::return_value_policy::reference_internal,
             "Extend the box to include the given location. If the location "
             "is invalid the box remains unchanged. If the box is invalid, it "
             "will contain only the location after the operation. "
             "Returns a reference to itself.")
        .def("extend",
             (osmium::Box& (osmium::Box::*)(osmium::Box const &))
                 &osmium::Box::extend,
             py::arg("box"),
             py::return_value_policy::reference_internal,
             "Extend the box to include the given box. If the box to be added "
             "is invalid the input box remains unchanged. If the input box is invalid, it "
             "will become equal to the box that was added. "
             "Returns a reference to itself.")
        .def("valid", &osmium::Box::valid,
             "Check if the box coordinates are defined and with the usual bounds.")
        .def("size", &osmium::Box::size,
             "Return the size in square degrees.")
        .def("contains", &osmium::Box::contains, py::arg("location"),
             "Check if the given location is inside the box.")\
    ;


    py::class_<osmium::Location>(m, "Location",
        "A geographic coordinate in WGS84 projection. A location doesn't "
         "necessarily have to be valid.")
        .def(py::init<>())
        .def(py::init<double, double>())
        .def(py::self == py::self)
        .def_property_readonly("x", &osmium::Location::x,
             "(read-only) X coordinate (longitude) as a fixed-point integer.")
        .def_property_readonly("y", &osmium::Location::y,
             "(read-only) Y coordinate (latitude) as a fixed-point integer.")
        .def_property_readonly("lon", &osmium::Location::lon,
             "(read-only) Longitude (x coordinate) as floating point number."
             "Raises an :py:class:`osmium.InvalidLocationError` when the "
             "location is invalid.")
        .def_property_readonly("lat", &osmium::Location::lat,
             "(read-only) Latitude (y coordinate) as floating point number."
             "Raises an :py:class:`osmium.InvalidLocationError` when the "
             "location is invalid.")
        .def("valid", &osmium::Location::valid,
             "Check that the location is a valid WGS84 coordinate, i.e. "
             "that it is within the usual bounds.")
        .def("lat_without_check", &osmium::Location::lat_without_check,
             "Return latitude (y coordinate) without checking if the location "
             "is valid.")
        .def("lon_without_check", &osmium::Location::lon_without_check,
             "Return longitude (x coordinate) without checking if the location "
             "is valid.")
    ;


    py::class_<TagIterator>(m, "CTagListIterator");
    py::class_<MemberIterator>(m, "CRelationMemberListIterator");
    py::class_<OuterRingIterator>(m, "COuterRingIterator");
    py::class_<InnerRingIterator>(m, "CInnerRingIterator");


    make_osm_object_class<pyosmium::COSMNode>(m, "COSMNode")
        .def("location", [](pyosmium::COSMNode const &o) { return o.get()->location(); })
    ;

    make_osm_object_class<pyosmium::COSMWay>(m, "COSMWay")
        .def("is_closed", [](pyosmium::COSMWay const &o) { return o.get()->is_closed(); })
        .def("ends_have_same_location", [](pyosmium::COSMWay const &o) { return o.get()->ends_have_same_location(); })
        .def("nodes", [](pyosmium::COSMWay const &o) { return &o.get()->nodes(); },
             py::return_value_policy::reference)
    ;


    make_osm_object_class<pyosmium::COSMRelation>(m, "COSMRelation")
        .def("members_size", [](pyosmium::COSMRelation const &o) { return o.get()->members().size(); })
        .def("members_begin", [](pyosmium::COSMRelation const &o) { return o.get()->members().cbegin(); })
        .def("members_next", [](pyosmium::COSMRelation const &o, MemberIterator &it)
            { return member_iterator_next(it, o.get()->members().cend()); })

    ;

    make_osm_object_class<pyosmium::COSMArea>(m, "COSMArea")
        .def("from_way", [](pyosmium::COSMArea const &o) { return o.get()->from_way(); })
        .def("orig_id", [](pyosmium::COSMArea const &o) { return o.get()->orig_id(); })
        .def("is_multipolygon", [](pyosmium::COSMArea const &o) { return o.get()->is_multipolygon(); })
        .def("num_rings", [](pyosmium::COSMArea const &o) { return o.get()->num_rings(); })
        .def("outer_begin", [](pyosmium::COSMArea const &o) { return o.get()->outer_rings().cbegin(); })
        .def("outer_next", [](pyosmium::COSMArea const &o, OuterRingIterator &it) {
            o.get();
            return ring_iterator_next<osmium::OuterRing>(it);
        },
             py::return_value_policy::reference)
        .def("inner_begin", [](pyosmium::COSMArea const &o, osmium::OuterRing const &ring)
            { return o.get()->inner_rings(ring).cbegin(); })
        .def("inner_next", [](pyosmium::COSMArea const &o, InnerRingIterator &it) {
            o.get();
            return ring_iterator_next<osmium::InnerRing>(it);
        },
             py::return_value_policy::reference)
    ;

    py::class_<pyosmium::COSMChangeset>(m, "COSMChangeset")
        .def("id", [](pyosmium::COSMChangeset const &o) { return o.get()->id(); })
        .def("uid", [](pyosmium::COSMChangeset const &o) { return o.get()->uid(); })
        .def("created_at", [](pyosmium::COSMChangeset const &o) { return o.get()->created_at(); })
        .def("closed_at", [](pyosmium::COSMChangeset const &o) { return o.get()->closed_at(); })
        .def("open", [](pyosmium::COSMChangeset const &o) { return o.get()->open(); })
        .def("num_changes", [](pyosmium::COSMChangeset const &o) { return o.get()->num_changes(); })
        .def("user", [](pyosmium::COSMChangeset const &o) { return o.get()->user(); })
        .def("user_is_anonymous", [](pyosmium::COSMChangeset const &o) { return o.get()->user_is_anonymous(); })
        .def("bounds", [](pyosmium::COSMChangeset const &o) { return o.get()->bounds(); })
        .def("tags_size", [](pyosmium::COSMChangeset const &o) { return o.get()->tags().size(); })
        .def("tags_get_value_by_key", [](pyosmium::COSMChangeset const &o, char const *key, char const *def)
            { return o.get()->tags().get_value_by_key(key, def); })
        .def("tags_has_key", [](pyosmium::COSMChangeset const &o, char const *key)
            { return o.get()->tags().has_key(key); })
        .def("tags_begin", [](pyosmium::COSMChangeset const &o) { return o.get()->tags().cbegin(); })
        .def("tags_next", [](pyosmium::COSMChangeset const &o, TagIterator &it)
            { return tag_iterator_next(it, o.get()->tags().cend()); })
        .def("is_valid", &pyosmium::COSMChangeset::is_valid)
    ;

    make_node_list<osmium::WayNodeList, pyosmium::COSMWay>(m, "CWayNodeList");
    make_node_list<osmium::OuterRing, pyosmium::COSMArea>(m, "COuterRing");
    make_node_list<osmium::InnerRing, pyosmium::COSMArea>(m, "CInnerRing");
}
