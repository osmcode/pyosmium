#ifndef PYOSMIUM_GENERIC_WRITER_HPP
#define PYOSMIUM_GENERIC_WRITER_HPP

#include <osmium/osm.hpp>
#include <osmium/io/any_output.hpp>
#include <osmium/io/writer.hpp>
#include <osmium/memory/buffer.hpp>

struct SimpleWriterWrap {

    SimpleWriterWrap(const char* filename)
    : writer(filename),
      buffer(1024*1024, osmium::memory::Buffer::auto_grow::yes)
    {}

    void add_osmium_object(const osmium::OSMObject& o) {
        buffer.add_item(o);
        flush_buffer();
    }

    void close() {
        writer(std::move(buffer));
        writer.close();
    }

private:
    void flush_buffer() {
        buffer.commit();

        if (buffer.committed() > 900*1024) {
            osmium::memory::Buffer new_buffer(1024*1024, osmium::memory::Buffer::auto_grow::yes);
            using std::swap;
            swap(buffer, new_buffer);
            writer(std::move(new_buffer));
        }
    }

    osmium::io::Writer writer;
    osmium::memory::Buffer buffer;
};

#endif // PYOSMIUM_GENERIC_WRITER_HPP
