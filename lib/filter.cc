/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#include <pybind11/pybind11.h>

#include "base_filter.h"


namespace py = pybind11;

PYBIND11_MODULE(_filter, m) {
    py::class_<pyosmium::BaseFilter, pyosmium::BaseHandler>(m, "BaseFilter")
        .def("enable_for", &pyosmium::BaseFilter::enable_for,
             py::arg("entities"),
             "Set the OSM types this filter should be used for.")
    ;

    pyosmium::init_empty_tag_filter(m);
    pyosmium::init_key_filter(m);
};

