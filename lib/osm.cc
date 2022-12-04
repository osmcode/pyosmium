#define PYBIND11_DETAILED_ERROR_MESSAGES
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include <osmium/osm/entity_bits.hpp>

#include "cast.h"
#include "osm_wrapper.h"

namespace py = pybind11;

class TagListIterator
{
public:
    TagListIterator(osmium::TagList const &t)
    : m_it(t.cbegin()), m_cend(t.cend()), m_size(t.size())
    {}

    py::object next()
    {
        if (m_it == m_cend)
            throw py::stop_iteration();

        static auto tag = py::module_::import("osmium.osm.types").attr("Tag");
        auto value = tag(m_it->key(), m_it->value());
        ++m_it;

        return value;
    }

    int size() const { return m_size; }

private:
    osmium::TagList::const_iterator m_it;
    osmium::TagList::const_iterator const m_cend;
    int const m_size;
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
        .def("nodes", [](COSMWay const &o) { return CNodeRefList(o.get()->nodes()); })
    ;


    py::class_<COSMRelation, COSMObject>(m, "COSMRelation");

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
        .def("tags_size", [](COSMChangeset const &o) { return o.get()->tags().size(); })
        .def("tags_get_value_by_key", [](COSMChangeset const &o, char const *key, char const *def)
            { return o.get()->tags().get_value_by_key(key, def); })
        .def("tags_has_key", [](COSMChangeset const &o, char const *key)
            { return o.get()->tags().has_key(key); })

    ;


    py::class_<CNodeRefList>(m, "CNodeRefList")
        .def("size", [](CNodeRefList const &o) { return o.get().size(); })
        .def("get", &CNodeRefList::get_item)
    ;

    m.def("get_undefined_coordinate", []() { return static_cast<int32_t>(osmium::Location::undefined_coordinate); });
}
