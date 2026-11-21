/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <osmium/osm.hpp>

#include <map>
#include <set>
#include <string>
#include <string_view>

#include "base_filter.h"

namespace py = pybind11;

namespace {

class TagFilter : public pyosmium::BaseFilter
{
public:
    TagFilter(py::args args)
    {
        if (args.empty()) {
            throw py::type_error{"Need tags to filter on."};
        }

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
            m_tags[tag[0].cast<std::string>()].insert(tag[1].cast<std::string>());
        }
    }

    bool filter(osmium::OSMObject const *o) override
    {
        return !has_matching_tag(o->tags());
    }

    bool filter_changeset(pyosmium::PyOSMChangeset &o) override
    {
        return !has_matching_tag(o.get()->tags());
    }

private:
    bool has_matching_tag(osmium::TagList const &tags) const
    {
        // With a single key, looking it up directly is faster than
        // walking all tags of the object.
        if (m_tags.size() == 1) {
            auto const &[key, values] = *m_tags.begin();
            char const *value = tags.get_value_by_key(key.c_str());
            return value && values.count(std::string_view{value}) > 0;
        }

        for (auto const &tag: tags) {
            auto const it = m_tags.find(std::string_view{tag.key()});
            if (it != m_tags.end()
                && it->second.count(std::string_view{tag.value()}) > 0
                // Like TagList::has_tag(), only the first tag with a key counts.
                && tags.get_value_by_key(tag.key()) == tag.value()) {
                return true;
            }
        }

        return false;
    }

    // std::less<> allows lookups by string_view without copying.
    std::map<std::string, std::set<std::string, std::less<>>, std::less<>> m_tags;
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
