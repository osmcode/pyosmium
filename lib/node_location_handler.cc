/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <osmium/index/map/all.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>

#include "base_handler.h"

namespace {

using LocationTable =
        osmium::index::map::Map<osmium::unsigned_object_id_type, osmium::Location>;
using NodeLocationHandler =
        osmium::handler::NodeLocationsForWays<LocationTable>;

class NodeLocationsForWays : public pyosmium::BaseHandler
{
public:
    NodeLocationsForWays(LocationTable &idx)
    : handler(idx)
    {
        m_enabled_for = osmium::osm_entity_bits::node
                        | osmium::osm_entity_bits::way;
    }

    bool node(pyosmium::PyOSMNode &o) override
    {
        handler.node(*(o.get()));
        return false;
    }

    bool way(pyosmium::PyOSMWay &o) override
    {
        if (apply_nodes_to_ways) {
            handler.way(*(o.get()));
        }
        return false;
    }

    bool get_apply_nodes_to_ways() const { return apply_nodes_to_ways; }

    void set_apply_nodes_to_ways(bool val) { apply_nodes_to_ways = val; }

    void ignore_errors() { handler.ignore_errors(); }

private:
    NodeLocationHandler handler;
    bool apply_nodes_to_ways = true;
};

} // namespace

namespace py = pybind11;

namespace pyosmium {

void init_node_location_handler(py::module &m)
{
    py::class_<NodeLocationsForWays, BaseHandler>(m, "NodeLocationsForWays")
        .def(py::init<LocationTable&>(), py::keep_alive<1, 2>())
        .def("ignore_errors", &NodeLocationsForWays::ignore_errors)
        .def_property("apply_nodes_to_ways",
                     &NodeLocationsForWays::get_apply_nodes_to_ways,
                     &NodeLocationsForWays::set_apply_nodes_to_ways)
    ;

}

} // namespace
