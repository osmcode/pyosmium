/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2026 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include <memory>

#include "base_filter.h"
#include "handler_chain.h"

namespace py = pybind11;

namespace {

class NotFilter : public pyosmium::BaseFilter
{
public:
    NotFilter(py::args args)
    : m_args(args), m_handlers(std::make_unique<pyosmium::HandlerChain>(m_args))
    {
        if (args.empty()) {
            throw py::type_error{"Need at least one filter to invert."};
        }
    }

    ~NotFilter() override
    {
        clear();
    }

    void flush() override
    {
        if (m_handlers) {
            m_handlers->flush();
        }
    }

    int traverse(visitproc visit, void *arg) const
    {
        Py_VISIT(m_args.ptr());
        return 0;
    }

    void clear()
    {
        // Destroy the borrowing chain before releasing its owners. Clear the
        // tuple before decref can run Python finalizers which reenter us.
        m_handlers.reset();
        Py_CLEAR(m_args.ptr());
    }

protected:
    bool filter_node(pyosmium::PyOSMNode &o) override
    {
        return !handlers().node(o);
    }

    bool filter_way(pyosmium::PyOSMWay &o) override
    {
        return !handlers().way(o);
    }

    bool filter_relation(pyosmium::PyOSMRelation &o) override
    {
        return !handlers().relation(o);
    }

    bool filter_area(pyosmium::PyOSMArea &o) override
    {
        return !handlers().area(o);
    }

    bool filter_changeset(pyosmium::PyOSMChangeset &o) override
    {
        return !handlers().changeset(o);
    }

private:
    pyosmium::HandlerChain &handlers()
    {
        if (!m_handlers) {
            throw py::value_error{"NotFilter's filter chain has been cleared."};
        }
        return *m_handlers;
    }

    // HandlerChain borrows its handlers. Keep all arguments alive, including
    // temporary native filters and Python callback objects, until after it dies.
    py::args m_args;
    std::unique_ptr<pyosmium::HandlerChain> m_handlers;
};

} // namespace

namespace pyosmium {

void init_not_filter(pybind11::module &m)
{
    py::class_<NotFilter, pyosmium::BaseFilter, BaseHandler>(m, "NotFilter",
        py::custom_type_setup([](PyHeapTypeObject *heap_type) {
            auto *type = &heap_type->ht_type;
            type->tp_flags |= Py_TPFLAGS_HAVE_GC;
            type->tp_traverse = [](PyObject *self, visitproc visit, void *arg) {
#if PY_VERSION_HEX >= 0x03090000
                Py_VISIT(Py_TYPE(self));
#endif
                // As in pybind11's custom_type_setup GC example, do not access
                // the C++ value until its holder is constructed. Use the
                // underlying check for compatibility with pybind11 2.9.
                auto *instance = reinterpret_cast<py::detail::instance *>(self);
                if (instance->get_value_and_holder().holder_constructed()) {
                    return py::cast<NotFilter &>(py::handle(self)).traverse(visit, arg);
                }
                return 0;
            };
            type->tp_clear = [](PyObject *self) {
                auto *instance = reinterpret_cast<py::detail::instance *>(self);
                if (instance->get_value_and_holder().holder_constructed()) {
                    py::cast<NotFilter &>(py::handle(self)).clear();
                }
                return 0;
            };
        }))
        .def(py::init<py::args>())
    ;
}

} // namespace
