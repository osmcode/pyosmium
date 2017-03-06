#include <osmium/visitor.hpp>
#include <osmium/index/map/all.hpp>
#include <osmium/handler/node_locations_for_ways.hpp>
#include <osmium/area/multipolygon_collector.hpp>
#include <osmium/area/assembler.hpp>

#include "generic_writer.hpp"
#include "generic_handler.hpp"
#include "merged_input.hpp"
#include "write_handler.hpp"

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
        "The most generic of OSM data handlers. For each data type "
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
             "handler for assembling multipolygons and areas from ways will\n"
             "be executed.")
        .def("apply_buffer", &SimpleHandlerWrap::apply_buffer,
              (arg("self"), arg("buffer"), arg("format"),
               arg("locations")=false, arg("idx")="sparse_mem_array"),
             "Apply the handler to a string buffer. The buffer must be a\n"
             "byte string.")
    ;
    def("apply", &apply_reader_simple<BaseHandler>,
        "Apply a chain of handlers.");
    def("apply", &apply_reader_simple<osmium::handler::NodeLocationsForWays<LocationTable>>);
    def("apply", &apply_reader_simple_with_location<LocationTable>);

    class_<SimpleWriterWrap, boost::noncopyable>("SimpleWriter",
        "The most generic class to write osmium objects into a file. The writer "
        "takes a file name as its mandatory parameter. The file must not yet "
        "exist. The file type to output is determined from the file extension. "
        "The second (optional) parameter is the buffer size. osmium caches the "
        "output data in an internal memory buffer before writing it on disk. This "
        "parameter allows changing the default buffer size of 4MB. Larger buffers "
        "are normally better but you should be aware that there are normally multiple "
        "buffers in use during the write process.",
        init<const char*, unsigned long>())
        .def(init<const char*>())
        .def("add_node", &SimpleWriterWrap::add_node,
             (arg("self"), arg("node")),
             "Add a new node to the file. The node may be an ``osmium.osm.Node`` object, "
             "an ``osmium.osm.mutable.Node`` object or any other Python object that "
             "implements the same attributes.")
        .def("add_way", &SimpleWriterWrap::add_way,
             (arg("self"), arg("way")),
             "Add a new way to the file. The way may be an ``osmium.osm.Way`` object, "
             "an ``osmium.osm.mutable.Way`` object or any other Python object that "
             "implements the same attributes.")
        .def("add_relation", &SimpleWriterWrap::add_relation,
             (arg("self"), arg("relation")),
             "Add a new relation to the file. The relation may be an "
             "``osmium.osm.Relation`` object, an ``osmium.osm.mutable.Way`` "
             "object or any other Python object that implements the same attributes.")
        .def("close", &SimpleWriterWrap::close,
             args("self"),
             "Flush the remaining buffers and close the writer. While it is not "
             "strictly necessary to call this function explicitly, it is still "
             "strongly recommended to close the writer as soon as possible, so "
             "that the buffer memory can be freed.")
    ;

    class_<WriteHandler, boost::noncopyable>("WriteHandler",
        "Handler function that writes all data directly to a file."
        "The handler takes a file name as its mandatory parameter. The file "
        "must not yet exist. The file type to output is determined from the "
        "file extension. "
        "The second (optional) parameter is the buffer size. osmium caches the "
        "output data in an internal memory buffer before writing it on disk. This "
        "parameter allows changing the default buffer size of 4MB. Larger buffers "
        "are normally better but you should be aware that there are normally multiple "
        "buffers in use during the write process.",
        init<const char*, unsigned long>())
        .def(init<const char*>())
        .def("close", &WriteHandler::close,
             args("self"),
             "Flush the remaining buffers and close the writer. While it is not "
             "strictly necessary to call this function explicitly, it is still "
             "strongly recommended to close the writer as soon as possible, so "
             "that the buffer memory can be freed.")
    ;

    class_<pyosmium::MergeInputReader, boost::noncopyable>("MergeInputReader",
        "Collects data from multiple input files and sorts and optionally "
        "deduplicates the data before applying it to a handler.")
        .def("apply", &pyosmium::MergeInputReader::apply,
            (arg("self"), arg("handler"), arg("simplify")=true),
            "Apply collected data to a handler. The data will be sorted first. "
            "If `simplify` is true (default) then duplicates will be eliminated "
            "and only the newest version of each object kept. After the data "
            "has been applied the buffer of the MergeInputReader is empty and "
            "new data can be added for the next round of application.")
        .def("apply_to_reader", &pyosmium::MergeInputReader::apply_to_reader,
            (arg("self"), arg("reader"), arg("writer"), arg("with_history")=false),
            "Apply the collected data to data from the given `reader` and write "
            "the result to `writer`. This function can be used to merge the diff "
            "data together with other OSM data (for example when updating a "
            "planet file. If `with_history` is true, then the collected data will "
            "be applied verbatim without removing duplicates. This is important "
            "when using OSM history files as input.")
        .def("add_file", &pyosmium::MergeInputReader::add_file,
            (arg("self"), arg("file")),
             "Add data from a file to the internal cache. The file type will be "
             "determined from the file extension.")
        .def("add_buffer", &pyosmium::MergeInputReader::add_buffer,
             (arg("self"), arg("buffer"), arg("format")),
             "Add data from a byte buffer. The format of the input data must "
             "be given in the `format` argument as a string. The data will be "
             "copied into internal buffers, so that the input buffer can be "
             "safely discarded after the function has been called.")
    ;
}
