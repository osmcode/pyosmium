#ifndef PYOSMIUM_CAST_H
#define PYOSMIUM_CAST_H

#include <pybind11/pybind11.h>
#include <datetime.h>
#include <chrono>

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

#if PY_VERSION_HEX >= 0x03040000
            auto ts = src.attr("timestamp")();
            value = (unsigned) ts.cast<double>();
#else
            // XXX terribly inefficient because of the double string conversion
            //     but the only painless method for converting a datetime
            //     in python < 3.3.
            auto ts = src.attr("strftime")("%Y-%m-%dT%H:%M:%SZ");

            value = osmium::Timestamp(ts.cast<std::string>());

#endif

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

#if PY_VERSION_HEX < 0x03000000
            return pydate;
#else
            auto utc = pybind11::module::import("datetime").attr("timezone").attr("utc");
            using namespace pybind11::literals;
            return pydate.attr("replace")("tzinfo"_a=utc).inc_ref();
#endif
        }

        PYBIND11_TYPE_CASTER(type, _("datetime.datetime"));
    };
}} // namespace pybind11::detail

#endif // PYOSMIUM_CAST_H
