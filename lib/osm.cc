
#include <cassert>
#include <time.h>
#include <boost/python.hpp>

#include <osmium/osm.hpp>
#include <osmium/osm/entity_bits.hpp>

#include "std_pair.hpp"


inline const char *get_tag_by_key(osmium::TagList const& obj, const char *value)
{
    const char* v = obj.get_value_by_key(value);
    if (!v)
        PyErr_SetString(PyExc_KeyError, "No tag with that key.");
    return v;
}

inline bool taglist_contains_tag(osmium::TagList const& obj, const char *value)
{
    const char* v = obj.get_value_by_key(value);
    return v;
}

inline const char member_item_type(osmium::RelationMember& obj)
{
    return item_type_to_char(obj.type());
}

// Converter for osmium::Timestamp -> datetime.datetime
struct Timestamp_to_python {
    static PyObject* convert(osmium::Timestamp const& s) {
#if PY_VERSION_HEX >= 0x03000000
        static auto fconv = boost::python::import("datetime").attr("datetime").attr("fromtimestamp");
        static boost::python::object utc = boost::python::import("datetime").attr("timezone").attr("utc");
        return boost::python::incref(fconv(s.seconds_since_epoch(), utc).ptr());
#else
        static auto fconv = boost::python::import("datetime").attr("datetime").attr("utcfromtimestamp");
        return boost::python::incref(fconv(s.seconds_since_epoch()).ptr());
#endif
    }
};


BOOST_PYTHON_MODULE(_osm)
{
    using namespace boost::python;
    docstring_options doc_options(true, true, false);

    to_python_converter<osmium::Timestamp, Timestamp_to_python>();
    std_pair_to_python_converter<int, int>();
    std_pair_to_python_converter<unsigned int, unsigned int>();
    std_pair_to_python_converter<unsigned long, unsigned long>();

    enum_<osmium::osm_entity_bits::type>("osm_entity_bits")
        .value("NOTHING", osmium::osm_entity_bits::nothing)
        .value("NODE", osmium::osm_entity_bits::node)
        .value("WAY", osmium::osm_entity_bits::way)
        .value("RELATION", osmium::osm_entity_bits::relation)
        .value("AREA", osmium::osm_entity_bits::area)
        .value("OBJECT", osmium::osm_entity_bits::object)
        .value("CHANGESET", osmium::osm_entity_bits::changeset)
        .value("ALL", osmium::osm_entity_bits::all)
    ;
    class_<osmium::Location>("Location",
        "A geographic coordinate in WGS84 projection. A location doesn't "
         "necessarily have to be valid.")
        .def(init<double, double>())
        .add_property("x", &osmium::Location::x,
                      "(read-only) X coordinate (longitude) as a fixed-point integer.")
        .add_property("y", &osmium::Location::y,
                      "(read-only) Y coordinate (latitude) as a fixed-point integer.")
        .add_property("lon", &osmium::Location::lon,
                      "(read-only) Longitude (x coordinate) as floating point number.")
        .add_property("lat", &osmium::Location::lat,
                      "(read-only) Latitude (y coordinate) as floating point number.")
        .def("valid", &osmium::Location::valid, args("self"),
                      "Check that the location is a valid WGS84 coordinate, i.e. "
                      "that it is within the usual bounds.")
    ;
    class_<osmium::Box>("Box",
        "A bounding box around a geographic area. It is defined by an "
        ":py:class:`osmium.osm.Location` for the bottem-left corner and an "
        "``osmium.osm.Location`` for the top-right corner. Those locations may "
        " be invalid in which case the box is considered invalid, too.")
        .def(init<double, double, double, double>())
        .def(init<osmium::Location, osmium::Location>())
        .add_property("bottom_left",
                      make_function(static_cast<osmium::Location& (osmium::Box::*)()>(&osmium::Box::bottom_left),
                                    return_value_policy<reference_existing_object>()),
             "(read-only) Bottom-left corner of the bounding box.")
        .add_property("top_right",
                      make_function(static_cast<osmium::Location& (osmium::Box::*)()>(&osmium::Box::top_right),
                                    return_value_policy<reference_existing_object>()),
             "(read-only) Top-right corner of the bounding box.")
        .def("extend",
              make_function(static_cast<osmium::Box& (osmium::Box::*)(const osmium::Location&)>(&osmium::Box::extend),
                            return_value_policy<reference_existing_object>()),
             //(arg("self"), arg("location")),
             "Extend the box to include the given location. If the location "
             "is invalid the box remains unchanged. If the box is invalid, it "
             "will contain only the location after the operation.")
        .def("extend",
              make_function(static_cast<osmium::Box& (osmium::Box::*)(const osmium::Box&)>(&osmium::Box::extend),
                            return_value_policy<reference_existing_object>()),
             //(arg("self"), arg("box")),
             "Extend the box to include the given box. If the box to be added "
             "is invalid the input box remains unchanged. If the input box is invalid, it "
             "will become equal to the box that was added.")
        .def("valid", &osmium::Box::valid, args("self"),
             "Check if the box coordinates are defined and with the usual bounds.")
        .def("size", &osmium::Box::size, args("self"),
             "Return the size in square degrees.")
        .def("contains", &osmium::Box::contains, (arg("self"), arg("location")),
             "Check if the given location is inside the box.")
    ;
    class_<osmium::Tag, boost::noncopyable>("Tag",
            "A single OSM tag.",
            no_init)
        .add_property("k", &osmium::Tag::key,
                      "(read-only) Tag key.")
        .add_property("v", &osmium::Tag::value,
                      "(read-only) Tag value.")
    ;
    class_<osmium::TagList, boost::noncopyable>("TagList",
        "A fixed list of tags. The list is exported as an unmutable, "
        "dictionary-like object where the keys are tag strings and the "
        "items are :py:class:`osmium.osm.Tag`.",
         no_init)
        .def("__len__", &osmium::TagList::size)
        .def("__getitem__", &get_tag_by_key)
        .def("__contains__", &taglist_contains_tag)
        .def("__iter__", iterator<osmium::TagList,return_internal_reference<>>())
    ;
    class_<osmium::NodeRef>("NodeRef",
        "A reference to a OSM node that also caches the nodes location.")
        .add_property("x", &osmium::NodeRef::x,
                      "(read-only) X coordinate (longitude) as a fixed-point integer.")
        .add_property("y", &osmium::NodeRef::y,
                      "(read-only) Y coordinate (latitude) as a fixed-point integer.")
        .add_property("lon", &osmium::NodeRef::lon,
                      "(read-only) Longitude (x coordinate) as floating point number.")
        .add_property("lat", &osmium::NodeRef::lat,
                      "(read-only) Latitude (y coordinate) as floating point number.")
        .add_property("ref", &osmium::NodeRef::ref,
                      "(read-only) Id of the referenced node.")
        .add_property("location", static_cast<osmium::Location (osmium::NodeRef::*)() const>(&osmium::NodeRef::location),
                      "(read-only) Node coordinates as a :py:class:`osmium.osm.Location` object.")
    ;
    class_<osmium::RelationMember, boost::noncopyable>("RelationMember",
        "Member of a relation.",
        no_init)
        .add_property("ref", static_cast<osmium::object_id_type (osmium::RelationMember::*)() const>(&osmium::RelationMember::ref),
                      "OSM ID of the object. Only unique within the type.")
        .add_property("type", &member_item_type,
                      "Type of object referenced, a node, way or relation.")
        .add_property("role", &osmium::RelationMember::role,
                      "The role of the member within the relation, a free-text string. "
                      "If no role is set then the string is empty.")
    ;
    class_<osmium::RelationMemberList, boost::noncopyable>("RelationMemberList",
           "An immutable  sequence of relation members :py:class:`osmium.osm.RelationMember`.",
           no_init)
        .def("__len__", &osmium::RelationMemberList::size)
        .def("__iter__", iterator<osmium::RelationMemberList,return_internal_reference<>>())
    ;
    class_<osmium::NodeRefList, boost::noncopyable>("NodeRefList",
        "A list of node references, implemented as "
        "an immutable sequence of :py:class:`osmium.osm.NodeRef`. This class "
        "is normally not used directly, use one of its subclasses instead.",
        no_init)
        .def("__len__", &osmium::NodeRefList::size)
        .def("__getitem__",
             make_function(static_cast<const osmium::NodeRef& (osmium::NodeRefList::*)(osmium::NodeRefList::size_type) const>(&osmium::NodeRefList::operator[]), return_value_policy<reference_existing_object>()))
        .def("__iter__", iterator<osmium::NodeRefList,return_internal_reference<>>())
        .def("is_closed", &osmium::NodeRefList::is_closed, args("self"),
             "True if the start and end node are the same (synonym for "
             "``ends_have_same_id``).")
        .def("ends_have_same_id", &osmium::NodeRefList::ends_have_same_id, args("self"),
             "True if the start and end node are exactly the same.")
        .def("ends_have_same_location", &osmium::NodeRefList::ends_have_same_location,
             args("self"),
             "True if the start and end node of the way are at the same location. "
             "Throws an exception if the location of one of the nodes is missing.")
    ;
    class_<osmium::WayNodeList, bases<osmium::NodeRefList>, boost::noncopyable>("WayNodeList",
        "List of nodes in a way. For its members see :py:class:`osmium.osm.NodeRefList`.",
        no_init)
    ;
    class_<osmium::OuterRing, bases<osmium::NodeRefList>, boost::noncopyable>("OuterRing",
        "List of nodes in an outer ring. For its members see :py:class:`osmium.osm.NodeRefList`.",
           no_init)
    ;
    class_<osmium::InnerRing, bases<osmium::NodeRefList>, boost::noncopyable>("InnerRing",
        "List of nodes in an inner ring. For its members see :py:class:`osmium.osm.NodeRefList`.",
           no_init)
    ;
    class_<osmium::OSMObject, boost::noncopyable>("OSMObject",
            "This is the base class for all OSM entity classes below and contains "
            "all common attributes.",
            no_init)
        .add_property("id", &osmium::OSMObject::id,
                      "(read-only) OSM id of the object.")
        .add_property("deleted", &osmium::OSMObject::deleted,
                      "(read-only) True if the object is no longer visible.")
        .add_property("visible", &osmium::OSMObject::visible,
                      "(read-only) True if the object is visible.")
        .add_property("version", &osmium::OSMObject::version,
                      "(read-only) Version number of the object.")
        .add_property("changeset", &osmium::OSMObject::changeset,
                      "(read-only) Id of changeset where this version of the "
                      "object was created.")
        .add_property("uid", &osmium::OSMObject::uid,
                      "(read-only) Id of the user that created this version "
                      "of the object. Only this ID uniquely identifies users.")
        .add_property("timestamp", &osmium::OSMObject::timestamp,
                      "(read-only) Date when this version has been created, "
                      "returned as a ``datetime.datetime``.")
        .add_property("user", &osmium::OSMObject::user,
                      "(read-only) Name of the user that created this version. "
                      "Be aware that user names can change, so that the same "
                      "user ID may appear with different names and vice versa. ")
        .add_property("tags", make_function(&osmium::OSMObject::tags,
                       return_value_policy<reference_existing_object>()),
                      "(read-only) List of tags describing the object. "
                      "See :py:class:`osmium.osm.TagList`.")
        .def("positive_id", &osmium::OSMObject::positive_id,
             arg("self"),
             "Get the absolute value of the id of this object.")
        .def("user_is_anonymous", &osmium::OSMObject::user_is_anonymous,
             arg("self"),
             "Check if the user is anonymous. If true, the uid does not uniquely "
             "identify a single user but only the group of all anonymous users "
             "in general.")
    ;
    class_<osmium::Node, bases<osmium::OSMObject>, boost::noncopyable>("Node",
            "Represents a single OSM node. It inherits from OSMObjects and "
            "adds a single attribute, the location.", no_init)
        .add_property("location", static_cast<osmium::Location (osmium::Node::*)() const>(&osmium::Node::location),
                      "The geographic coordinates of the node. "
                      "See :py:class:`osmium.osm.Location`.")
    ;
    class_<osmium::Way, bases<osmium::OSMObject>, boost::noncopyable>("Way", 
        "Represents a OSM way. It inherits the attributes from OSMObjects and "
        "adds an ordered list of nodes that describes the way.",
        no_init)
        .add_property("nodes",
                      make_function(static_cast<const osmium::WayNodeList& (osmium::Way::*)() const>(&osmium::Way::nodes),
                      return_value_policy<reference_existing_object>()),
                      "(read-only) Ordered list of nodes. See :py:class:`osmium.osm.WayNodeList`.")
        .def("is_closed", &osmium::Way::is_closed, args("self"),
             "True if the start and end node are the same (synonym for "
             "``ends_have_same_id``).")
        .def("ends_have_same_id", &osmium::Way::ends_have_same_id, args("self"),
             "True if the start and end node are exactly the same.")
        .def("ends_have_same_location", &osmium::Way::ends_have_same_location,
             args("self"),
             "True if the start and end node of the way are at the same location."
             "Throws an exception if the location of one of the nodes is missing.")
    ;
    class_<osmium::Relation, bases<osmium::OSMObject>, boost::noncopyable>("Relation",
                 "Represents a OSM relation. It inherits the attributes from OSMObjects "
                 "and adds an ordered list of members.",
                 no_init)
        .add_property("members", 
                      make_function(static_cast<const osmium::RelationMemberList& (osmium::Relation::*)() const>(&osmium::Relation::members),
                      return_value_policy<reference_existing_object>()),
                      "(read-only) Ordered list of relation members. "
                      "See :py:class:`osmium.osm.RelationMemberList`")
    ;
    class_<osmium::Area, bases<osmium::OSMObject>, boost::noncopyable>("Area",
            "Areas are a special kind of meta-object representing a polygon. "
            "They can either be derived from closed ways or from relations "
            "that represent multipolygons. They also inherit the attributes "
            "of OSMObjects and in addition contain polygon geometries. Areas have "
            "their own unique id space. This is computed as the OSM id times 2 "
            "and for relations 1 is added,",
            no_init)
        .def("from_way", &osmium::Area::from_way, args("self"),
             "Return true if the area was created from a way, false if it was "
             "created from a relation of multipolygon type.")
        .def("orig_id", &osmium::Area::orig_id, args("self"),
             "Compute the original OSM id of this object. Note that this is not "
             "necessarily unique because the object might be a way or relation "
             "which have an overlapping id space.")
        .def("is_multipolygon", &osmium::Area::is_multipolygon, args("self"),
             "Return true if this area is a true multipolygon, i.e. it consists "
             "of multiple outer rings.")
        .def("num_rings", &osmium::Area::num_rings, args("self"),
             "Return a tuple with the number of outer rings and inner rings.")
        .def("outer_rings", 
              range<return_internal_reference<> >(
                &osmium::Area::cbegin<osmium::OuterRing>,
                &osmium::Area::cend<osmium::OuterRing>),
             "Return an iterator over all outer rings of the multipolygon.")
        .def("inner_rings", 
              range<return_internal_reference<> >(
                &osmium::Area::cbegin<osmium::InnerRing>,
                &osmium::Area::cend<osmium::InnerRing>),
             "Return an iterator over all inner rings of the multipolygon.")
    ;
    class_<osmium::Changeset, boost::noncopyable>("Changeset",
           "A changeset description.",
           no_init)
        .add_property("id", &osmium::Changeset::id,
                      "(read-only) Unique ID of the changeset.")
        .add_property("uid", &osmium::Changeset::uid,
                      "(read-only) User ID of the changeset creator.")
        .add_property("created_at", &osmium::Changeset::created_at,
                      "(read-only) Timestamp when the changeset was first opened.")
        .add_property("closed_at", &osmium::Changeset::closed_at,
                      "(read-only) Timestamp when the changeset was finalized. May be "
                      "None when the changeset is still open.")
        .add_property("open", &osmium::Changeset::open,
                      "(read-only) True when the changeset is still open.")
        .add_property("num_changes", &osmium::Changeset::num_changes,
                      "(read-only) The total number of objects changed in this "
                      "Changeset.")
        .add_property("bounds",
                      make_function(static_cast<const osmium::Box& (osmium::Changeset::*)() const>(&osmium::Changeset::bounds),
                      return_value_policy<reference_existing_object>()),
                      "(read-only) The bounding box of the area that was edited.")
        .add_property("user", &osmium::Changeset::user,
                      "(read-only) Name of the user that created the changeset. "
                      "Be aware that user names can change, so that the same "
                      "user ID may appear with different names and vice versa. ")
        .add_property("tags", make_function(&osmium::Changeset::tags,
                       return_value_policy<reference_existing_object>()),
                      "(read-only) List of tags describing the changeset. "
                      "See :py:class:`osmium.osm.TagList`.")
        .def("user_is_anonymous", &osmium::Changeset::user_is_anonymous,
               arg("self"),
               "Check if the user anonymous. If true, the uid does not uniquely "
               "identify a single user but only the group of all anonymous users "
               "in general.")
    ;
}
