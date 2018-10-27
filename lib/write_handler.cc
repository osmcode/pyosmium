#include <pybind11/pybind11.h>

#include <osmium/io/any_output.hpp>
#include <osmium/io/writer.hpp>
#include <osmium/memory/buffer.hpp>

#include "base_handler.h"

namespace {

class WriteHandler : public BaseHandler
{
    enum { BUFFER_WRAP = 4096 };

public:
    WriteHandler(const char* filename, size_t bufsz=4096*1024)
    : writer(filename),
      buffer(bufsz < 2 * BUFFER_WRAP ? 2 * BUFFER_WRAP : bufsz,
             osmium::memory::Buffer::auto_grow::yes)
    {}

    virtual ~WriteHandler()
    { close(); }

    osmium::osm_entity_bits::type enabled_callbacks() override
    { return osmium::osm_entity_bits::all; }

    void node(const osmium::Node* o) override
    {
        buffer.add_item(*o);
        flush_buffer();
    }

    void way(const osmium::Way* o) override
    {
        buffer.add_item(*o);
        flush_buffer();
    }

    void relation(const osmium::Relation* o) override
    {
        buffer.add_item(*o);
        flush_buffer();
    }

    void changeset(const osmium::Changeset*) override {}

    void area(const osmium::Area*) override {}

    void close()
    {
        if (buffer) {
            writer(std::move(buffer));
            writer.close();
            buffer = osmium::memory::Buffer();
        }
    }

private:
    void flush_buffer()
    {
        buffer.commit();

        if (buffer.committed() > buffer.capacity() - BUFFER_WRAP) {
            osmium::memory::Buffer new_buffer(buffer.capacity(), osmium::memory::Buffer::auto_grow::yes);
            using std::swap;
            swap(buffer, new_buffer);
            writer(std::move(new_buffer));
        }
    }

    osmium::io::Writer writer;
    osmium::memory::Buffer buffer;
};

}

namespace py = pybind11;

void init_write_handler(pybind11::module &m)
{
    py::class_<WriteHandler, BaseHandler>(m, "WriteHandler",
        "Handler function that writes all data directly to a file."
        "The handler takes a file name as its mandatory parameter. The file "
        "must not yet exist. The file type to output is determined from the "
        "file extension. "
        "The second (optional) parameter is the buffer size. osmium caches the "
        "output data in an internal memory buffer before writing it on disk. This "
        "parameter allows changing the default buffer size of 4MB. Larger buffers "
        "are normally better but you should be aware that there are normally multiple "
        "buffers in use during the write process.")
        .def(py::init<const char*, unsigned long>())
        .def(py::init<const char*>())
        .def("close", &WriteHandler::close,
             "Flush the remaining buffers and close the writer. While it is not "
             "strictly necessary to call this function explicitly, it is still "
             "strongly recommended to close the writer as soon as possible, so "
             "that the buffer memory can be freed.")
    ;
}
