#ifndef PYOSMIUM_OSMIUM_MODULE_H
#define PYOSMIUM_OSMIUM_MODULE_H

#include <pybind11/pybind11.h>

void init_merge_input_reader(pybind11::module &m);
void init_write_handler(pybind11::module &m);
void init_simple_writer(pybind11::module &m);

#endif // PYOSMIUM_OSMIUM_MODULE_H
