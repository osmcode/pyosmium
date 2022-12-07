#ifndef PYOSMIUM_OSM_BASE_OBJECTS_HPP
#define PYOSMIUM_OSM_BASE_OBJECTS_HPP

#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>

class COSMObject {
public:
    osmium::OSMObject const *get_object() const {
        auto const *obj = object_ptr();
        if (!obj) {
            throw std::runtime_error{"Access to removed object"};
        }
        return obj;
    }

    bool is_valid() const { return object_ptr(); }

protected:
    virtual osmium::OSMObject const *object_ptr() const = 0;
};

template <typename T>
class COSMDerivedObject : public COSMObject {
public:
    COSMDerivedObject(T *obj) : m_obj(obj) {}

    T const *get() const {
        if (!m_obj) {
            throw std::runtime_error{"Access to removed object"};
        }
        return m_obj;
    }

    void invalidate() { m_obj = nullptr; }

protected:
    osmium::OSMObject const *object_ptr() const override { return m_obj; }

private:
    T *m_obj;
};

using COSMNode = COSMDerivedObject<osmium::Node const>;
using COSMWay = COSMDerivedObject<osmium::Way const>;
using COSMRelation = COSMDerivedObject<osmium::Relation const>;
using COSMArea = COSMDerivedObject<osmium::Area const>;


class COSMChangeset {
public:
    COSMChangeset(osmium::Changeset const *obj) : m_obj(obj) {}

    osmium::Changeset const *get() const {
        if (!m_obj) {
            throw std::runtime_error{"Access to removed object"};
        }
        return m_obj;
    }

    void invalidate() { m_obj = nullptr; }

    bool is_valid() const { return m_obj; }

private:
    osmium::Changeset const *m_obj;
};

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

        static auto const node_ref_t = pybind11::module_::import("osmium.osm.types").attr("NodeRef");

        return node_ref_t(node.location(), node.ref());
     }

private:
    ImplClass *m_obj;
};

using CWayNodeList = CNodeRefList<osmium::WayNodeList>;
using COuterRing = CNodeRefList<osmium::OuterRing>;
using CInnerRing = CNodeRefList<osmium::InnerRing>;


#endif //PYOSMIUM_OSM_BASE_OBJECTS_HPP
