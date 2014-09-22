#include <osmium/handler.hpp>

using namespace boost::python;

class VirtualHandler : public osmium::handler::Handler {

public:

virtual void node(const osmium::Node&) const {
}

virtual void way(const osmium::Way&) const {
}

virtual void relation(const osmium::Relation&) const {
}

virtual void changeset(const osmium::Changeset&) const {
}


};



struct SimpleHandlerWrap: VirtualHandler, wrapper<VirtualHandler> {

    void node(const osmium::Node& node) const {
        if (override f = this->get_override("node"))
            f(boost::ref(node));
    }

    void default_node(const osmium::Node&) const {
    }

    void way(const osmium::Way& way) const {
        if (override f = this->get_override("way"))
            f(boost::ref(way));
    }

    void default_way(const osmium::Way&) const {
    }

    void relation(const osmium::Relation& rel) const {
        if (override f = this->get_override("relation"))
            f(boost::ref(rel));
    }

    void default_relation(const osmium::Relation&) const {
    }

    void changeset(const osmium::Changeset& cs) const {
        if (override f = this->get_override("changeset"))
            f(boost::ref(cs));
    }

    void default_changeset(const osmium::Changeset&) const {
    }

};
