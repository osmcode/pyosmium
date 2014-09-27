#include <boost/python.hpp>

#include <osmium/osm.hpp>
#include <osmium/index/map/sparse_table.hpp>

//class SparseLocationHandler : osmium::index::map::SparseTable<osmium::unsigned_object_id_type, osmium::Location> {}

BOOST_PYTHON_MODULE(_index)
{
    using namespace boost::python;

    class_<osmium::index::map::SparseTable<osmium::unsigned_object_id_type, osmium::Location>, boost::noncopyable>("SparseLocationTable")
    ;
}

