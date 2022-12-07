#ifndef PYOSMIUM_OSM_HELPER_HPP
#define PYOSMIUM_OSM_HELPER_HPP

template <typename T>
class CNodeRefList {
    using ImplClass = T const;

public:
    CNodeRefList(ImplClass *list) : m_obj(list) {}

    ImplClass *get() const {
        return m_obj;
    }

    pybind11::object get_item(Py_ssize_t idx) const
     {
        auto sz = m_obj->size();

        osmium::NodeRefList::size_type iout =
            (idx >= 0 ? idx : (Py_ssize_t) sz + idx);

        if (iout >= sz || iout < 0) {
            throw pybind11::index_error("Bad index.");
        }

        auto const &node = (*m_obj)[iout];

        static auto node_ref_t = pybind11::module_::import("osmium.osm.types").attr("NodeRef");

        return node_ref_t(node.location(), node.ref());
     }

private:
    ImplClass *m_obj;
};

using CWayNodeList = CNodeRefList<osmium::WayNodeList>;
using COuterRing = CNodeRefList<osmium::OuterRing>;
using CInnerRing = CNodeRefList<osmium::InnerRing>;

#endif //PYOSMIUM_OSM_HELPER_HPP
