#include <boost/python.hpp>

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


BOOST_PYTHON_MODULE(_osm)
{
    using namespace boost::python;
    docstring_options doc_options(true, true, false);

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
    class_<osmium::Timestamp>("Timestamp")
        .def("__str__", &osmium::Timestamp::to_iso)
    ;
    class_<osmium::Location>("Location")
        .def(init<double, double>())
        .add_property("x", &osmium::Location::x)
        .add_property("y", &osmium::Location::y)
        .add_property("lon", &osmium::Location::lon)
        .add_property("lat", &osmium::Location::lat)
        .def("valid", &osmium::Location::valid)
    ;
    class_<osmium::Tag, boost::noncopyable>("Tag", no_init)
        .add_property("k", &osmium::Tag::key)
        .add_property("v", &osmium::Tag::value)
    ;
    class_<osmium::TagList, boost::noncopyable>("TagList", no_init)
        .def("__len__", &osmium::TagList::size)
        .def("__getitem__", &get_tag_by_key)
        .def("__contains__", &taglist_contains_tag)
        .def("__iter__", iterator<osmium::TagList,return_internal_reference<>>())
    ;
    class_<osmium::NodeRef>("NodeRef")
        .add_property("x", &osmium::NodeRef::x)
        .add_property("y", &osmium::NodeRef::y)
        .add_property("lon", &osmium::NodeRef::lon)
        .add_property("lat", &osmium::NodeRef::lat)
        .add_property("ref", &osmium::NodeRef::ref)
        .add_property("location", static_cast<osmium::Location (osmium::NodeRef::*)() const>(&osmium::NodeRef::location))
    ;
    class_<osmium::WayNodeList, boost::noncopyable>("WayNodeList", no_init)
        .def("__len__", &osmium::WayNodeList::size)
        .def("__getitem__", &osmium::WayNodeList::operator[], return_value_policy<reference_existing_object>())
        .def("__iter__", iterator<osmium::WayNodeList,return_internal_reference<>>())
    ;
    class_<osmium::RelationMember, boost::noncopyable>("RelationMember", no_init)
        .add_property("ref", static_cast<osmium::object_id_type (osmium::RelationMember::*)() const>(&osmium::RelationMember::ref))
        .add_property("type", &member_item_type)
        .add_property("role", &osmium::RelationMember::role)
    ;
    class_<osmium::RelationMemberList, boost::noncopyable>("RelationMemberList", no_init)
        .def("__len__", &osmium::RelationMemberList::size)
        .def("__iter__", iterator<osmium::RelationMemberList,return_internal_reference<>>())
    ;
    class_<osmium::Changeset, boost::noncopyable>("Changeset", no_init)
    ;
    class_<osmium::OSMObject, boost::noncopyable>("OSMObject",
            "This is the base class for all OSM entity classes below and contains "
            "all common attributes.",
            no_init)
        .add_property("id", &osmium::OSMObject::id)
        .add_property("deleted", &osmium::OSMObject::deleted)
        .add_property("visible", &osmium::OSMObject::visible)
        .add_property("version", &osmium::OSMObject::version)
        .add_property("changeset", &osmium::OSMObject::changeset)
        .add_property("uid", &osmium::OSMObject::uid)
        .add_property("timestamp", &osmium::OSMObject::timestamp)
        .add_property("user", &osmium::OSMObject::user)
        .add_property("tags", make_function(&osmium::OSMObject::tags,
                       return_value_policy<reference_existing_object>()))
        .def("positive_id", &osmium::OSMObject::positive_id,
             arg("self"),
             "Get the absolute value of the id of this object.")
        .def("user_is_anonymous", &osmium::OSMObject::user_is_anonymous)
    ;
    class_<osmium::Node, bases<osmium::OSMObject>, boost::noncopyable>("Node",
            "Represents a single OSM node. It inherits from OSMObjects and "
            "adds a single attribute: the location.", no_init)
        .add_property("location", static_cast<osmium::Location (osmium::Node::*)() const>(&osmium::Node::location))
    ;
    class_<osmium::Way, bases<osmium::OSMObject>, boost::noncopyable>("Way", no_init)
        .add_property("nodes", 
                      make_function(static_cast<const osmium::WayNodeList& (osmium::Way::*)() const>(&osmium::Way::nodes),
                      return_value_policy<reference_existing_object>()))
        .def("is_closed", &osmium::Way::is_closed)
        .def("ends_have_same_id", &osmium::Way::ends_have_same_id)
        .def("ends_have_same_location", &osmium::Way::ends_have_same_location)
    ;
    class_<osmium::Relation, bases<osmium::OSMObject>, boost::noncopyable>("Relation", no_init)
        .add_property("members", 
                      make_function(static_cast<const osmium::RelationMemberList& (osmium::Relation::*)() const>(&osmium::Relation::members),
                      return_value_policy<reference_existing_object>()))
    ;
    class_<osmium::Area, bases<osmium::OSMObject>, boost::noncopyable>("Area", no_init)
    ;
}
