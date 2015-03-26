#ifndef PYOSMIUM_STD_PAIR_HPP
#define PYOSMIUM_STD_PAIR_HPP

// Borrowed from Boost Python examples.
// Copyright Ralf W. Grosse-Kunstleve 2002-2004. Distributed under the Boost
// Software License, Version 1.0.

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/to_python_converter.hpp>

namespace { // Avoid cluttering the global namespace.

  // Converts a std::pair instance to a Python tuple.
  template <typename T1, typename T2>
  struct std_pair_to_tuple
  {
    static PyObject* convert(std::pair<T1, T2> const& p)
    {
      return boost::python::incref(
        boost::python::make_tuple(p.first, p.second).ptr());
    }
    static PyTypeObject const *get_pytype () {return &PyTuple_Type; }
  };

  // Helper for convenience.
  template <typename T1, typename T2>
  struct std_pair_to_python_converter
  {
    std_pair_to_python_converter()
    {
      boost::python::to_python_converter<
        std::pair<T1, T2>,
        std_pair_to_tuple<T1, T2>,
        true //std_pair_to_tuple has get_pytype
        >();
    }
  };

} // namespace anonymous

#endif
