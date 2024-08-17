/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>

#include "base_filter.h"

namespace py = pybind11;

namespace {

class KeyFilter : public pyosmium::BaseFilter
{
public:
    KeyFilter(py::args args)
    {
        if (args.empty()) {
            throw py::type_error{"Need keys to filter on."};
        }

        m_keys.reserve(args.size());
        for (auto const &arg: args) {
            if (!py::isinstance<py::str>(arg)) {
                throw py::type_error{"Arguments must be strings."};
            }

            m_keys.push_back(arg.cast<std::string>());
        }
    }

    bool filter(osmium::OSMObject const *o) override
    {
        auto const &tags = o->tags();
        for (auto const &key: m_keys) {
            if (tags.has_key(key.c_str())) {
                return false;
            }
        }

        return true;
    }

    bool filter_changeset(pyosmium::PyOSMChangeset &o) override
    {
        auto const &tags = o.get()->tags();
        for (auto const &key: m_keys) {
            if (tags.has_key(key.c_str())) {
                return false;
            }
        }

        return true;
    }

private:
    std::vector<std::string> m_keys;
};

} // namespace

namespace pyosmium {

void init_key_filter(pybind11::module &m)
{
    py::class_<KeyFilter, pyosmium::BaseFilter, BaseHandler>(m, "KeyFilter")
        .def(py::init<py::args>())
    ;
}

} // namespace
