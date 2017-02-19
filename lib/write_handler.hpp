#ifndef PYOSMIUM_WRITE_HANDLER_HPP
#define PYOSMIUM_WRITE_HANDLER_HPP

#include <osmium/io/any_output.hpp>
#include <osmium/io/writer.hpp>
#include <osmium/memory/buffer.hpp>

#include <boost/python.hpp>

#include "generic_handler.hpp"

class WriteHandler : public BaseHandler, public boost::python::wrapper<BaseHandler> {
    enum { BUFFER_WRAP = 4096 };

public:
    WriteHandler(const char* filename, size_t bufsz=4096*1024)
    : writer(filename),
      buffer(bufsz < 2*BUFFER_WRAP ? 2*BUFFER_WRAP : bufsz, osmium::memory::Buffer::auto_grow::yes)
    {}

    virtual ~WriteHandler() {
        close();
    }

    void node(const osmium::Node& o) {
        buffer.add_item(o);
        flush_buffer();
    }

    void way(const osmium::Way& o) {
        buffer.add_item(o);
        flush_buffer();
    }

    void relation(const osmium::Relation& o) {
        buffer.add_item(o);
        flush_buffer();
    }

    void changeset(const osmium::Changeset&) {}

    void area(const osmium::Area&) {}

    void close() {
        if (buffer) {
            writer(std::move(buffer));
            writer.close();
            buffer = osmium::memory::Buffer();
        }
    }

private:
    void flush_buffer() {
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

#endif // PYOSMIUM_WRITE_HANDLER_HPP
