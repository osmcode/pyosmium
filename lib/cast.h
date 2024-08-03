/* SPDX-License-Identifier: BSD-2-Clause
 *
 * This file is part of pyosmium. (https://osmcode.org/pyosmium/)
 *
 * Copyright (C) 2024 Sarah Hoffmann <lonvia@denofr.de> and others.
 * For a full list of authors see the git log.
 */
#ifndef PYOSMIUM_CAST_H
#define PYOSMIUM_CAST_H

#include <datetime.h>
#include <chrono>

#include <pybind11/pybind11.h>
#include <osmium/osm.hpp>

namespace pybind11 { namespace detail {
    template <> struct type_caster<osmium::Timestamp> {
    public:
        using type = osmium::Timestamp;

        bool load(handle src, bool) {
            // Lazy initialise the PyDateTime import
            if (!PyDateTimeAPI) { PyDateTime_IMPORT; }

            if (!src) {
                return false;
            }

            if (pybind11::isinstance<pybind11::str>(src)) {
                value = osmium::Timestamp(src.cast<std::string>());
                return true;
            }

            if (!PyDateTime_Check(src.ptr())) {
                return false;
            }

            auto ts = src.attr("timestamp")();
            value = (unsigned) ts.cast<double>();

            return true;
        }

        static handle cast(type const &src, return_value_policy, handle)
        {
            using namespace std::chrono;
            // Lazy initialise the PyDateTime import
            if (!PyDateTimeAPI) { PyDateTime_IMPORT; }

            std::time_t tt = src.seconds_since_epoch();
            std::tm localtime = *std::gmtime(&tt);
            handle pydate = PyDateTime_FromDateAndTime(localtime.tm_year + 1900,
                                                       localtime.tm_mon + 1,
                                                       localtime.tm_mday,
                                                       localtime.tm_hour,
                                                       localtime.tm_min,
                                                       localtime.tm_sec,
                                                       0);

            static auto utc = module::import("datetime").attr("timezone").attr("utc");
            using namespace literals;
            handle with_utc = pydate.attr("replace")("tzinfo"_a=utc).inc_ref();
            pydate.dec_ref();
            return with_utc;
        }

        PYBIND11_TYPE_CASTER(type, _("datetime.datetime"));
    };
}} // namespace pybind11::detail

namespace pyosmium {

template <typename T>
T const *try_cast(pybind11::object o) {
    auto const inner = pybind11::getattr(o, "_pyosmium_data", pybind11::none());

    if (pybind11::isinstance<T>(inner)) {
        return inner.cast<T const *>();
    }

    return nullptr;
}


template <typename T>
T const &cast(pybind11::object o) {
    return o.attr("_pyosmium_data").cast<T const &>();
}


template <typename T>
T const *try_cast_list(pybind11::object o) {
    auto const ward = pybind11::getattr(o, "_pyosmium_data", pybind11::none());

    if (ward.is_none()) {
        return nullptr;
    }

    auto const valid_func = pybind11::getattr(ward, "is_valid", pybind11::none());

    if (valid_func.is_none() || !valid_func().cast<bool>()) {
        return nullptr;
    }

    auto const inner = pybind11::getattr(o, "_list", pybind11::none());

    if (pybind11::isinstance<T>(inner)) {
        return inner.cast<T const *>();
    }

    return nullptr;
}


template <typename T>
T const &cast_list(pybind11::object const &o) {
    if (!o.attr("_pyosmium_data").attr("is_valid")().cast<bool>()) {
        throw std::runtime_error{"Illegal access to removed OSM object"};
    }

    return o.attr("_list").cast<T const &>();
}

} // namespace

#endif // PYOSMIUM_CAST_H
