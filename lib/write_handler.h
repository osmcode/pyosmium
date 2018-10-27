#ifndef PYOSMIUM_WRITE_HANDLER_HPP
#define PYOSMIUM_WRITE_HANDLER_HPP

#include <osmium/io/any_output.hpp>
#include <osmium/io/writer.hpp>
#include <osmium/memory/buffer.hpp>

#include "base_handler.h"

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

#endif // PYOSMIUM_WRITE_HANDLER_HPP
