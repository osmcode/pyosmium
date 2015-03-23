#include <time.h>
#include <boost/python.hpp>
#include <datetime.h>

#include <osmium/osm.hpp>
#include <osmium/osm/entity_bits.hpp>


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
        struct tm tm;
        time_t sse = s.seconds_since_epoch();
        gmtime_r(&sse, &tm);

        return boost::python::incref(
                PyDateTime_FromDateAndTime(tm.tm_year + 1900, tm.tm_mon + 1,
                                           tm.tm_mday, tm.tm_hour, tm.tm_min,
                                           tm.tm_sec, 0));
    }
};


BOOST_PYTHON_MODULE(_osm)
{
    PyDateTime_IMPORT;
    using namespace boost::python;
    docstring_options doc_options(true, true, false);

    to_python_converter<osmium::Timestamp, Timestamp_to_python>();

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
         "have to be necessarily valid.")
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
    class_<osmium::WayNodeList, boost::noncopyable>("WayNodeList",
        "A sequence of node references :py:class:`osmium.osm.NodeRef`.",
        no_init)
        .def("__len__", &osmium::WayNodeList::size)
        .def("__getitem__", &osmium::WayNodeList::operator[], return_value_policy<reference_existing_object>())
        .def("__iter__", iterator<osmium::WayNodeList,return_internal_reference<>>())
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
           "A sequence of relation members :py:class:`osmium.osm.RelationMember`.",
           no_init)
        .def("__len__", &osmium::RelationMemberList::size)
        .def("__iter__", iterator<osmium::RelationMemberList,return_internal_reference<>>())
    ;
    class_<osmium::Changeset, boost::noncopyable>("Changeset",
           "A changeset description, currently unimplemented.",
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
                      "List of tags describing the object. "
                      "See :py:class:`osmium.osm.TagList`.")
        .def("positive_id", &osmium::OSMObject::positive_id,
             arg("self"),
             "Get the absolute value of the id of this object.")
        .def("user_is_anonymous", &osmium::OSMObject::user_is_anonymous,
             arg("self"),
             "Check if the user anonymous. If true, the uid does not uniquely "
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
             "True if the start and end node of the way are at the same location.")
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
            "of OSMObjects and in addition contain polygon geometries. The "
            "geometries are not exported to Python at the moment. Areas have "
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
    ;
}
