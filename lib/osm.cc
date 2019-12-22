#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>
#include <osmium/osm/entity_bits.hpp>

#include "cast.h"

namespace py = pybind11;

class TagIterator
{
public:
    TagIterator(osmium::Tag const &t, py::object r)
    : tag(t), ref(r)
    {}

    char const *next()
    {
        switch (index) {
            case 0:
                ++index;
                return tag.key();
            case 1:
                ++index;
                return tag.value();
        };

        throw py::stop_iteration();
    }

private:
    osmium::Tag const &tag;
    py::object ref; // keep a reference
    size_t index = 0;
};


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

    py::class_<osmium::Location>(m, "Location",
        "A geographic coordinate in WGS84 projection. A location doesn't "
         "necessarily have to be valid.")
        .def(py::init<>())
        .def(py::init<double, double>())
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
             "will contain only the location after the operation.")
        .def("extend",
             (osmium::Box& (osmium::Box::*)(osmium::Box const &))
                 &osmium::Box::extend,
             py::arg("box"),
             py::return_value_policy::reference_internal,
             "Extend the box to include the given box. If the box to be added "
             "is invalid the input box remains unchanged. If the input box is invalid, it "
             "will become equal to the box that was added.")
        .def("valid", &osmium::Box::valid,
             "Check if the box coordinates are defined and with the usual bounds.")
        .def("size", &osmium::Box::size,
             "Return the size in square degrees.")
        .def("contains", &osmium::Box::contains, py::arg("location"),
             "Check if the given location is inside the box.")
    ;

    py::class_<TagIterator>(m, "TagIterator")
        .def("__iter__", [](TagIterator &it) -> TagIterator& { return it; })
        .def("__next__", &TagIterator::next)
        .def("__len__", [](TagIterator const &it) { return 2; })
    ;

    py::class_<osmium::Tag>(m, "Tag",
        "A single OSM tag.")
        .def_property_readonly("k", &osmium::Tag::key,
             "(read-only) Tag key.")
        .def_property_readonly("v", &osmium::Tag::value,
             "(read-only) Tag value.")
        .def("__iter__", [](py::object s)
                         { return TagIterator(s.cast<osmium::Tag const &>(), s); })
    ;

    py::class_<osmium::TagList>(m, "TagList",
        "A fixed list of tags. The list is exported as an unmutable, "
        "dictionary-like object where the keys are tag strings and the "
        "items are :py:class:`osmium.osm.Tag`.")
        .def("__len__", &osmium::TagList::size)
        .def("__getitem__", [](osmium::TagList const &obj, const char *key)
            {
                if (!key) {
                    throw py::key_error("Key 'None' not allowed.");
                }

                const char* v = obj.get_value_by_key(key);
                if (!v) {
                    throw py::key_error("No tag with that key.");
                }
                return v;
            })
        .def("__contains__", [](osmium::TagList const &obj, const char *key)
                             { return key && obj.has_key(key); })
        .def("__iter__", [](osmium::TagList const &obj)
                         { return py::make_iterator(obj.begin(), obj.end()); },
                         py::keep_alive<0, 1>())
        .def("get", &osmium::TagList::get_value_by_key,
             py::arg("key"), py::arg("default"))
        .def("get", [](osmium::TagList const &obj, const char *key)
                    { return key ? obj.get_value_by_key(key) : nullptr; })
    ;

    py::class_<osmium::NodeRef>(m, "NodeRef",
        "A reference to a OSM node that also caches the nodes location.")
        .def_property_readonly("x", &osmium::NodeRef::x,
             "(read-only) X coordinate (longitude) as a fixed-point integer.")
        .def_property_readonly("y", &osmium::NodeRef::y,
             "(read-only) Y coordinate (latitude) as a fixed-point integer.")
        .def_property_readonly("lon", &osmium::NodeRef::lon,
             "(read-only) Longitude (x coordinate) as floating point number.")
        .def_property_readonly("lat", &osmium::NodeRef::lat,
             "(read-only) Latitude (y coordinate) as floating point number.")
        .def_property_readonly("ref", &osmium::NodeRef::ref,
             "(read-only) Id of the referenced node.")
        .def_property_readonly("location",
                               (osmium::Location (osmium::NodeRef::*)() const)
                                 &osmium::NodeRef::location,
             "(read-only) Node coordinates as a :py:class:`osmium.osm.Location` object.")
    ;

    py::class_<osmium::RelationMember>(m, "RelationMember",
        "Member of a relation.")
        .def_property_readonly("ref", 
                               (osmium::object_id_type (osmium::RelationMember::*)() const)
                                   &osmium::RelationMember::ref,
             "OSM ID of the object. Only unique within the type.")
        .def_property_readonly("type", [](osmium::RelationMember& obj)
                                       { return item_type_to_char(obj.type()); },
             "Type of object referenced, a node, way or relation.")
        .def_property_readonly("role", &osmium::RelationMember::role,
             "The role of the member within the relation, a free-text string. "
             "If no role is set then the string is empty.")
    ;

    py::class_<osmium::RelationMemberList>(m, "RelationMemberList",
        "An immutable  sequence of relation members "
        ":py:class:`osmium.osm.RelationMember`.")
        .def("__len__", &osmium::RelationMemberList::size)
        .def("__iter__", [](osmium::RelationMemberList const &obj)
                         { return py::make_iterator(obj.begin(), obj.end()); },
                         py::keep_alive<0, 1>())
    ;

    py::class_<osmium::NodeRefList>(m, "NodeRefList",
        "A list of node references, implemented as "
        "an immutable sequence of :py:class:`osmium.osm.NodeRef`. This class "
        "is normally not used directly, use one of its subclasses instead.")
        .def("__len__", &osmium::NodeRefList::size)
        .def("__getitem__", [](osmium::NodeRefList const &list, ssize_t idx)
             {
                auto sz = list.size();
                osmium::NodeRefList::size_type iout =
                    (idx >= 0 ? idx : (ssize_t) sz + idx);

                if (iout >= sz || iout < 0) {
                    throw py::index_error("Bad index.");
                }

                return list[iout];
             },
             py::return_value_policy::reference_internal)
        .def("__iter__", [](osmium::NodeRefList const &obj)
                         { return py::make_iterator(obj.begin(), obj.end()); },
                         py::keep_alive<0, 1>())
        .def("is_closed", &osmium::NodeRefList::is_closed,
             "True if the start and end node are the same (synonym for "
             "``ends_have_same_id``).")
        .def("ends_have_same_id", &osmium::NodeRefList::ends_have_same_id,
             "True if the start and end node are exactly the same.")
        .def("ends_have_same_location", &osmium::NodeRefList::ends_have_same_location,
             "True if the start and end node of the way are at the same location. "
             "Expects that the coordinates of the way nodes have been loaded "
             "(see :py:func:`osmium.SimpleHandler.apply_buffer` and "
             ":py:func:`osmium.SimpleHandler.apply_file`). "
             "If the locations are not present then the function returns always true.")
    ;

    py::class_<osmium::WayNodeList, osmium::NodeRefList>(m, "WayNodeList",
        "List of nodes in a way. "
        "For its members see :py:class:`osmium.osm.NodeRefList`.")
    ;

    py::class_<osmium::OuterRing, osmium::NodeRefList>(m, "OuterRing",
        "List of nodes in an outer ring. "
        "For its members see :py:class:`osmium.osm.NodeRefList`.")
    ;

    py::class_<osmium::InnerRing, osmium::NodeRefList>(m, "InnerRing",
        "List of nodes in an inner ring. "
        "For its members see :py:class:`osmium.osm.NodeRefList`.")
    ;

    using InnerRingRange =
             osmium::memory::ItemIteratorRange<osmium::InnerRing const>;
    py::class_<InnerRingRange>(m, "InnerRingIterator",
        "Iterator over inner rings.")
        .def("__iter__", [](InnerRingRange const &obj)
                         { return py::make_iterator(obj.begin(), obj.end()); },
                         py::keep_alive<0, 1>())
    ;

    py::class_<osmium::OSMObject>(m, "OSMObject",
        "This is the base class for all OSM entity classes below and contains "
        "all common attributes.")
        .def_property_readonly("id", &osmium::OSMObject::id,
             "(read-only) OSM id of the object.")
        .def_property_readonly("deleted", &osmium::OSMObject::deleted,
             "(read-only) True if the object is no longer visible.")
        .def_property_readonly("visible", &osmium::OSMObject::visible,
             "(read-only) True if the object is visible.")
        .def_property_readonly("version", &osmium::OSMObject::version,
             "(read-only) Version number of the object.")
        .def_property_readonly("changeset", &osmium::OSMObject::changeset,
             "(read-only) Id of changeset where this version of the "
             "object was created.")
        .def_property_readonly("uid", &osmium::OSMObject::uid,
             "(read-only) Id of the user that created this version "
             "of the object. Only this ID uniquely identifies users.")
        .def_property_readonly("timestamp", &osmium::OSMObject::timestamp,
             "(read-only) Date when this version has been created, "
             "returned as a ``datetime.datetime``.")
        .def_property_readonly("user", &osmium::OSMObject::user,
             "(read-only) Name of the user that created this version. "
             "Be aware that user names can change, so that the same "
             "user ID may appear with different names and vice versa. ")
        .def_property_readonly("tags", &osmium::OSMObject::tags,
                               py::return_value_policy::reference_internal,
             "(read-only) List of tags describing the object. "
             "See :py:class:`osmium.osm.TagList`.")
        .def("positive_id", &osmium::OSMObject::positive_id,
             "Get the absolute value of the id of this object.")
        .def("user_is_anonymous", &osmium::OSMObject::user_is_anonymous,
             "Check if the user is anonymous. If true, the uid does not uniquely "
             "identify a single user but only the group of all anonymous users "
             "in general.")
    ;

    py::class_<osmium::Node, osmium::OSMObject>(m, "Node",
        "Represents a single OSM node. It inherits from OSMObjects and "
        "adds a single attribute, the location.")
        .def_property_readonly("location",
                               (osmium::Location (osmium::Node::*)() const)
                                   &osmium::Node::location,
             "The geographic coordinates of the node. "
             "See :py:class:`osmium.osm.Location`.")
    ;

    py::class_<osmium::Way, osmium::OSMObject>(m, "Way",
        "Represents a OSM way. It inherits the attributes from OSMObjects and "
        "adds an ordered list of nodes that describes the way.")
        .def_property_readonly("nodes",
                               (const osmium::WayNodeList& (osmium::Way::*)() const)
                                   &osmium::Way::nodes,
                               py::return_value_policy::reference_internal,
             "(read-only) Ordered list of nodes. "
             "See :py:class:`osmium.osm.WayNodeList`.")
        .def("is_closed", &osmium::Way::is_closed,
             "True if the start and end node are the same (synonym for "
             "``ends_have_same_id``).")
        .def("ends_have_same_id", &osmium::Way::ends_have_same_id,
             "True if the start and end node are exactly the same.")
        .def("ends_have_same_location", &osmium::Way::ends_have_same_location,
             "True if the start and end node of the way are at the same location."
             "Expects that the coordinates of the way nodes have been loaded "
             "(see :py:func:`osmium.SimpleHandler.apply_buffer` and "
             ":py:func:`osmium.SimpleHandler.apply_file`). "
             "If the locations are not present then the function returns always true.")
    ;

    py::class_<osmium::Relation, osmium::OSMObject>(m, "Relation",
        "Represents a OSM relation. It inherits the attributes from OSMObjects "
        "and adds an ordered list of members.")
        .def_property_readonly("members", 
                               (const osmium::RelationMemberList& (osmium::Relation::*)() const)
                                   &osmium::Relation::members,
                               py::return_value_policy::reference_internal,
             "(read-only) Ordered list of relation members. "
             "See :py:class:`osmium.osm.RelationMemberList`.")
    ;

    py::class_<osmium::Area, osmium::OSMObject>(m, "Area",
        "Areas are a special kind of meta-object representing a polygon. "
        "They can either be derived from closed ways or from relations "
        "that represent multipolygons. They also inherit the attributes "
        "of OSMObjects and in addition contain polygon geometries. Areas have "
        "their own unique id space. This is computed as the OSM id times 2 "
        "and for relations 1 is added,")
        .def("from_way", &osmium::Area::from_way,
             "Return true if the area was created from a way, false if it was "
             "created from a relation of multipolygon type.")
        .def("orig_id", &osmium::Area::orig_id,
             "Compute the original OSM id of this object. Note that this is not "
             "necessarily unique because the object might be a way or relation "
             "which have an overlapping id space.")
        .def("is_multipolygon", &osmium::Area::is_multipolygon,
             "Return true if this area is a true multipolygon, i.e. it consists "
             "of multiple outer rings.")
        .def("num_rings", &osmium::Area::num_rings,
             "Return a tuple with the number of outer rings and inner rings.")
        .def("outer_rings", [](osmium::Area const &a)
                            { return py::make_iterator(a.cbegin<osmium::OuterRing>(),
                                                       a.cend<osmium::OuterRing>()); },
                            py::keep_alive<0, 1>(),
             "Return an iterator over all outer rings of the multipolygon.")
        .def("inner_rings", &osmium::Area::inner_rings,
                            py::keep_alive<0, 1>(),
             py::arg("outer_ring"),
             "Return an iterator over all inner rings of the multipolygon.")
    ;

    py::class_<osmium::Changeset>(m, "Changeset",
        "A changeset description.")
        .def_property_readonly("id", &osmium::Changeset::id,
             "(read-only) Unique ID of the changeset.")
        .def_property_readonly("uid", &osmium::Changeset::uid,
             "(read-only) User ID of the changeset creator.")
        .def_property_readonly("created_at", &osmium::Changeset::created_at,
             "(read-only) Timestamp when the changeset was first opened.")
        .def_property_readonly("closed_at", &osmium::Changeset::closed_at,
             "(read-only) Timestamp when the changeset was finalized. May be "
             "None when the changeset is still open.")
        .def_property_readonly("open", &osmium::Changeset::open,
             "(read-only) True when the changeset is still open.")
        .def_property_readonly("num_changes", &osmium::Changeset::num_changes,
             "(read-only) The total number of objects changed in this Changeset.")
        .def_property_readonly("bounds",
                               (osmium::Box const& (osmium::Changeset::*)() const)
                                   &osmium::Changeset::bounds,
                               py::return_value_policy::reference_internal,
             "(read-only) The bounding box of the area that was edited.")
        .def_property_readonly("user", &osmium::Changeset::user,
             "(read-only) Name of the user that created the changeset. "
             "Be aware that user names can change, so that the same "
             "user ID may appear with different names and vice versa. ")
        .def_property_readonly("tags", &osmium::Changeset::tags,
                               py::return_value_policy::reference_internal,
             "(read-only) List of tags describing the changeset. "
             "See :py:class:`osmium.osm.TagList`.")
        .def("user_is_anonymous", &osmium::Changeset::user_is_anonymous,
             "Check if the user anonymous. If true, the uid does not uniquely "
             "identify a single user but only the group of all anonymous users "
             "in general.")
    ;
}
