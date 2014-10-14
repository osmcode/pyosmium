#include <boost/python.hpp>

#include <osmium/osm.hpp>
#include <osmium/index/map/sparse_table.hpp>
#include <osmium/index/map/mmap_vector_anon.hpp>
#include <osmium/index/map/mmap_vector_file.hpp>

using namespace boost::python;

typedef osmium::index::map::SparseTable<osmium::unsigned_object_id_type, osmium::Location> SparseLocationTable;
typedef osmium::index::map::DenseMapFile<osmium::unsigned_object_id_type, osmium::Location> DenseLocationMapFile;


BOOST_PYTHON_MODULE(_index)
{

    class_<SparseLocationTable, boost::noncopyable>("SparseLocationTable")
        .def("set", &SparseLocationTable::set)
        .def("get", &SparseLocationTable::get)
        .def("size", &SparseLocationTable::size)
        .def("used_memory", &SparseLocationTable::used_memory)
        .def("clear", &SparseLocationTable::clear)
    ;

    class_<DenseLocationMapFile, boost::noncopyable>("DenseLocationMapFile", 
           init<int>())
        .def("set", &DenseLocationMapFile::set)
        .def("get", &DenseLocationMapFile::get)
        .def("size", &DenseLocationMapFile::size)
        .def("used_memory", &DenseLocationMapFile::used_memory)
        .def("clear", &DenseLocationMapFile::clear)
    ;
}

