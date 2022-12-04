#define PYBIND11_DETAILED_ERROR_MESSAGES
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include <osmium/osm/entity_bits.hpp>

#include "cast.h"
#include "osm_base_objects.h"
#include "osm_helper.h"

namespace py = pybind11;



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


    py::class_<TagListIterator>(m, "TagListIterator")
        .def("__iter__", [](TagListIterator &it) -> TagListIterator& { return it; })
        .def("__next__", &TagListIterator::next)
        .def("__len__", &TagListIterator::size)
    ;


    py::class_<RelationMemberListIterator>(m, "RelationMemberListIterator")
        .def("__iter__", [](RelationMemberListIterator &it) -> RelationMemberListIterator& { return it; })
        .def("__next__", &RelationMemberListIterator::next)
        .def("__len__", &RelationMemberListIterator::size)
    ;


    py::class_<COSMObject>(m, "COSMObject")
        .def("id", [](COSMObject const &o) { return o.get_object()->id(); })
        .def("deleted", [](COSMObject const &o) { return o.get_object()->deleted(); })
        .def("visible", [](COSMObject const &o) { return o.get_object()->visible(); })
        .def("version", [](COSMObject const &o) { return o.get_object()->version(); })
        .def("changeset", [](COSMObject const &o) { return o.get_object()->changeset(); })
        .def("uid", [](COSMObject const &o) { return o.get_object()->uid(); })
        .def("timestamp", [](COSMObject const &o) { return o.get_object()->timestamp(); })
        .def("user", [](COSMObject const &o) { return o.get_object()->user(); })
        .def("positive_id", [](COSMObject const &o) { return o.get_object()->positive_id(); })
        .def("user_is_anonymous", [](COSMObject const &o) { return o.get_object()->user_is_anonymous(); })
        .def("tags_size", [](COSMObject const &o) { return o.get_object()->tags().size(); })
        .def("tags_get_value_by_key", [](COSMObject const &o, char const *key, char const *def)
            { return o.get_object()->tags().get_value_by_key(key, def); })
        .def("tags_has_key", [](COSMObject const &o, char const *key)
            { return o.get_object()->tags().has_key(key); })
        .def("tags_iter", [](COSMObject const &o) { return TagListIterator(o.get_object()->tags()); })
        .def("is_valid", &COSMObject::is_valid)
    ;

    py::class_<COSMNode, COSMObject>(m, "COSMNode")
        .def("location", [](COSMNode const &o) { return o.get()->location(); })
    ;

    py::class_<COSMWay, COSMObject>(m, "COSMWay")
        .def("is_closed", [](COSMWay const &o) { return o.get()->is_closed(); })
        .def("ends_have_same_id", [](COSMWay const &o) { return o.get()->ends_have_same_id(); })
        .def("ends_have_same_location", [](COSMWay const &o) { return o.get()->ends_have_same_location(); })
        .def("nodes", [](COSMWay const &o) { return CNodeRefList(&(o.get()->nodes())); })
    ;


    py::class_<COSMRelation, COSMObject>(m, "COSMRelation")
        .def("members_size", [](COSMRelation const &o) { return o.get()->members().size(); })
        .def("members_iter", [](COSMRelation const &o) { return RelationMemberListIterator(o.get()->members()); })
    ;

    py::class_<COSMArea, COSMObject>(m, "COSMArea")
        .def("from_way", [](COSMArea const &o) { return o.get()->from_way(); })
        .def("orig_id", [](COSMArea const &o) { return o.get()->orig_id(); })
        .def("is_multipolygon", [](COSMArea const &o) { return o.get()->is_multipolygon(); })
        .def("num_rings", [](COSMArea const &o) { return o.get()->num_rings(); })
    ;

    py::class_<COSMChangeset>(m, "COSMChangeset")
        .def("id", [](COSMChangeset const &o) { return o.get()->id(); })
        .def("uid", [](COSMChangeset const &o) { return o.get()->uid(); })
        .def("created_at", [](COSMChangeset const &o) { return o.get()->created_at(); })
        .def("closed_at", [](COSMChangeset const &o) { return o.get()->closed_at(); })
        .def("open", [](COSMChangeset const &o) { return o.get()->open(); })
        .def("num_changes", [](COSMChangeset const &o) { return o.get()->num_changes(); })
        .def("user", [](COSMChangeset const &o) { return o.get()->user(); })
        .def("user_is_anonymous", [](COSMChangeset const &o) { return o.get()->user_is_anonymous(); })
        .def("bounds", [](COSMChangeset const &o) { return o.get()->bounds(); })
        .def("tags_size", [](COSMChangeset const &o) { return o.get()->tags().size(); })
        .def("tags_get_value_by_key", [](COSMChangeset const &o, char const *key, char const *def)
            { return o.get()->tags().get_value_by_key(key, def); })
        .def("tags_has_key", [](COSMChangeset const &o, char const *key)
            { return o.get()->tags().has_key(key); })
        .def("tags_iter", [](COSMChangeset const &o) { return TagListIterator(o.get()->tags()); })
        .def("is_valid", &COSMChangeset::is_valid)
    ;


    py::class_<CNodeRefList>(m, "CNodeRefList")
        .def("size", [](CNodeRefList const &o) { return o.get()->size(); })
        .def("get", &CNodeRefList::get_item)
    ;

    m.def("get_undefined_coordinate", []() { return static_cast<int32_t>(osmium::Location::undefined_coordinate); });
}
