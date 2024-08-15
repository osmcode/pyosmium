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

PYBIND11_MODULE(filter, m) {
    pyosmium::init_empty_tag_filter(m);
    pyosmium::init_key_filter(m);
    pyosmium::init_tag_filter(m);
    pyosmium::init_entity_filter(m);
    pyosmium::init_id_filter(m);
    pyosmium::init_geo_interface_filter(m);
};

