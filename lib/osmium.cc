#include <boost/python.hpp>

#include <osmium/visitor.hpp>
#include <osmium/index/map/all.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>
#include <osmium/area/multipolygon_collector.hpp>
#include <osmium/area/assembler.hpp>

#include "generic_handler.hpp"
#include "generic_writer.hpp"

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

void translator1(osmium::invalid_location const&) {
    PyErr_SetString(invalidLocationExceptionType, "Invalid location");
}

void translator2(osmium::not_found const&) {
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
    docstring_options doc_options(true, true, false);

    invalidLocationExceptionType = createExceptionClass("InvalidLocationError", PyExc_RuntimeError);
    register_exception_translator<osmium::invalid_location>(&translator1);

    notFoundExceptionType = createExceptionClass("NotFoundError", PyExc_KeyError);
    register_exception_translator<osmium::not_found>(&translator2);

    class_<osmium::handler::NodeLocationsForWays<LocationTable>, boost::noncopyable>("NodeLocationsForWays", 
            init<LocationTable&>())
        .def("ignore_errors", &osmium::handler::NodeLocationsForWays<LocationTable>::ignore_errors)
    ;

    class_<SimpleHandlerWrap, boost::noncopyable>("SimpleHandler",
        "A handler implements custom processing of OSM data. For each data type "
        "a callback can be implemented where the object is processed. Note that "
        "all objects that are handed into the handler are only readable and are "
        "only valid until the end of the callback is reached. Any data that "
        "should be retained must be copied into other data structures.")
        .def("node", &BaseHandler::node, &SimpleHandlerWrap::default_node,
             (arg("self"), arg("node")),
             "Handler called for node objects.")
        .def("way", &BaseHandler::way, &SimpleHandlerWrap::default_way,
             (arg("self"), arg("way")),
             "Handler called for way objects. If the geometry of the way is "
             "needed then ``locations`` must be set to true when calling "
             "apply_file.")
        .def("relation", &BaseHandler::relation, &SimpleHandlerWrap::default_relation,
             (arg("self"), arg("relation")),
             "Handler called for relation objects.")
        .def("changeset", &BaseHandler::changeset, &SimpleHandlerWrap::default_changeset,
             (arg("self"), arg("changeset")),
             "Handler called for changeset objects.")
        .def("area", &BaseHandler::area, &SimpleHandlerWrap::default_area,
             (arg("self"), arg("area")),
             "Handler called for area objects.")
        .def("apply_file", &SimpleHandlerWrap::apply_file,
              (arg("self"), arg("filename"),
               arg("locations")=false, arg("idx")="sparse_mem_array"),
             "Apply the handler to the given file. If locations is true, then\n"
             "a location handler will be applied before, which saves the node\n"
             "positions. In that case, the type of this position index can be\n"
             "further selected in idx. If an area callback is implemented, then\n"
             "the file will be scanned twice and a location handler and a\n"
             "handler for assembling multipolygones and areas from ways will\n"
             "be executed.")
    ;
    def("apply", &apply_reader_simple<BaseHandler>,
        "Apply a chain of handlers.");
    def("apply", &apply_reader_simple<osmium::handler::NodeLocationsForWays<LocationTable>>);
    def("apply", &apply_reader_simple_with_location<LocationTable>);

    class_<SimpleWriterWrap, boost::noncopyable>("SimpleWriter",
        "The most basic class to write osmium objects into a file.",
        init<const char*, unsigned long>())
        .def(init<const char*>())
        .def("add_node", &SimpleWriterWrap::add_node,
             (arg("self"), arg("node")),
             "Add a new node to the file. The node must be a class object "
             "with the same attributes as the osmium Node object. Tags are "
             "expected in a dictionary-like object.")
        .def("add_way", &SimpleWriterWrap::add_way,
             (arg("self"), arg("way")),
             "Add a new way to the file.")
        .def("add_relation", &SimpleWriterWrap::add_relation,
             (arg("self"), arg("relation")),
             "Add a new relation to the file.")
        .def("close", &SimpleWriterWrap::close,
             args("self"),
             "Close the writer.")
    ;
}
