# Thread safety

Object instances of pyosmium are not thread-safe to modify. If you share
objects like an index, you have to protect write accesses to these objects.
Concurrent reads are safe.

The library functions themselves are all reentrant and may be used safely from
different threads.

### Free-threaded Python

Starting with version 4.1, Pyosmium has experimental support for Python
runtimes with GIL disabled. See the
[Python Free-Threading Guide](https://py-free-threading.github.io/)
for more information.

The restrictions mentioned above still apply: write accesses on object need
to be protected by exclusive locks when using them in multi-threaded context.
