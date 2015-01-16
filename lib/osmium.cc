#include <boost/python.hpp>

#include <osmium/visitor.hpp>
#include <osmium/index/map/all.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>
#include <osmium/area/multipolygon_collector.hpp>
#include <osmium/area/assembler.hpp>

#include "generic_handler.hpp"

template <typename T>
void apply_reader_simple(osmium::io::Reader &rd, T &h) {
    osmium::apply(rd, h);
}


template <typename T>
void apply_reader_simple_with_location(osmium::io::Reader &rd,
                         osmium::handler::NodeLocationsForWays<T> &l,
                         BaseHandler &h) {
    osmium::apply(rd, l, h);
}

PyObject *invalidLocationExceptionType = NULL;
PyObject *notFoundExceptionType = NULL;

void translator1(osmium::invalid_location const& x) {
    PyErr_SetString(invalidLocationExceptionType, "Invalid location");
}

void translator2(osmium::not_found const& x) {
    PyErr_SetString(notFoundExceptionType, "Element not found in index");
}

PyObject* createExceptionClass(const char* name, PyObject* baseTypeObj = PyExc_Exception)
{
    using std::string;
    namespace bp = boost::python;

    string scopeName = bp::extract<string>(bp::scope().attr("__name__"));
    string qualifiedName0 = scopeName + "." + name;
    char* qualifiedName1 = const_cast<char*>(qualifiedName0.c_str());

    PyObject* typeObj = PyErr_NewException(qualifiedName1, baseTypeObj, 0);
    if(!typeObj) bp::throw_error_already_set();
    bp::scope().attr(name) = bp::handle<>(bp::borrowed(typeObj));
    return typeObj;
}

#include "index.cc"

BOOST_PYTHON_MODULE(_osmium)
{
    using namespace boost::python;

    invalidLocationExceptionType = createExceptionClass("InvalidLocationError", PyExc_RuntimeError);
    register_exception_translator<osmium::invalid_location>(&translator1);

    notFoundExceptionType = createExceptionClass("NotFoundError", PyExc_KeyError);
    register_exception_translator<osmium::not_found>(&translator2);

    class_<osmium::handler::NodeLocationsForWays<LocationTable>, boost::noncopyable>("NodeLocationsForWays", 
            init<LocationTable&>())
        .def("ignore_errors", &osmium::handler::NodeLocationsForWays<LocationTable>::ignore_errors)
    ;

    class_<SimpleHandlerWrap, boost::noncopyable>("SimpleHandler")
        .def("node", &BaseHandler::node, &SimpleHandlerWrap::default_node)
        .def("way", &BaseHandler::way, &SimpleHandlerWrap::default_way)
        .def("relation", &BaseHandler::relation, &SimpleHandlerWrap::default_relation)
        .def("changeset", &BaseHandler::changeset, &SimpleHandlerWrap::default_changeset)
        .def("area", &BaseHandler::area, &SimpleHandlerWrap::default_area)
        .def("apply_file", &SimpleHandlerWrap::apply_file,
              ("filename", arg("locations")=false, arg("idx")="sparse_mem_array"),
             "Apply the handler to the given file. If locations is true, then\n"
             "a location handler will be applied before, which saves the node\n"
             "positions. In that case, the type of this position index can be\n"
             "further selected in idx. If an area callback is implemented, then\n"
             "the file will be scanned twice and a location handler and a\n"
             "handler for assembling multipolygones and areas from ways will\n"
             "be executed.")
    ;
    def("apply", &apply_reader_simple<BaseHandler>);
    def("apply", &apply_reader_simple<osmium::handler::NodeLocationsForWays<LocationTable>>);
    def("apply", &apply_reader_simple_with_location<LocationTable>);
}
