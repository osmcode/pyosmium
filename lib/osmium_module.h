/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2023 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#ifndef PYOSMIUM_OSMIUM_MODULE_H
#define PYOSMIUM_OSMIUM_MODULE_H

#include <pybind11/pybind11.h>

void init_merge_input_reader(pybind11::module &m);
void init_write_handler(pybind11::module &m);
void init_simple_writer(pybind11::module &m);

#endif // PYOSMIUM_OSMIUM_MODULE_H
