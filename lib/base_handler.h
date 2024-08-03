/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#ifndef PYOSMIUM_BASE_HANDLER_HPP
#define PYOSMIUM_BASE_HANDLER_HPP

#include <osmium/handler.hpp>

namespace pyosmium {

class BaseHandler : public osmium::handler::Handler
{
public:
    virtual ~BaseHandler() = default;

    // work around pybind's bad copy policy
    // (see https://github.com/pybind/pybind11/issues/1241)
    void node(const osmium::Node &o) { node(&o); }
    void way(osmium::Way &o) { way(&o); }
    void relation(const osmium::Relation &o) { relation(&o); }
    void changeset(const osmium::Changeset &o) { changeset(&o); }
    void area(const osmium::Area &o) { area(&o); }

    // Actual handler functions.
    // All object handlers return a boolean which indicates if
    // processing is finished (true) or should be continued with the next
    // handler (false).
    virtual bool node(const osmium::Node*) { return false; }
    virtual bool way(osmium::Way *) { return false; }
    virtual bool relation(const osmium::Relation*) { return false; }
    virtual bool changeset(const osmium::Changeset*) { return false; }
    virtual bool area(const osmium::Area*)  { return false; }

    virtual void flush() {}
};

} // namespace

#endif // PYOSMIUM_BASE_HANDLER_HPP
