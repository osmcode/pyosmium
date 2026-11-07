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

struct Tag
{
    Tag(std::string k, std::string v)
    : key(std::move(k)), value(std::move(v))
    {}

    std::string key;
    std::string value;
};

class TagFilter : public pyosmium::BaseFilter
{
public:
    TagFilter(py::args args)
    {
        if (args.empty()) {
            throw py::type_error{"Need tags to filter on."};
        }

        m_tags.reserve(args.size());
        for (auto const &arg: args) {
            if (!py::isinstance<py::tuple>(arg)) {
                throw py::type_error{"Each tag must be a tuple of (key, value)."};
            }
            auto const tag = arg.cast<py::tuple>();
            if (py::len(tag) != 2
                || !py::isinstance<py::str>(tag[0])
                || !py::isinstance<py::str>(tag[1])) {
                throw py::type_error{"Each tag must be a tuple of (key, value)."};
            }
            m_tags.emplace_back(tag[0].cast<std::string>(),
                                tag[1].cast<std::string>());
        }
    }

    bool filter(osmium::OSMObject const *o) override
    {
        auto const &tags = o->tags();
        for (auto const &tag: m_tags) {
            if (tags.has_tag(tag.key.c_str(), tag.value.c_str())) {
                return false;
            }
        }

        return true;
    }

    bool filter_changeset(pyosmium::PyOSMChangeset &o) override
    {
        auto const &tags = o.get()->tags();
        for (auto const &tag: m_tags) {
            if (tags.has_tag(tag.key.c_str(), tag.value.c_str())) {
                return false;
            }
        }

        return true;
    }

private:
    std::vector<Tag> m_tags;
};

}

namespace pyosmium {

void init_tag_filter(pybind11::module &m)
{
    py::class_<TagFilter, pyosmium::BaseFilter, BaseHandler>(m, "TagFilter")
        .def(py::init<py::args>())
    ;
}

} // namespace
