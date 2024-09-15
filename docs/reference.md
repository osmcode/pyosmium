# Overview

This section lists all functions and classes that pyosmium implements
for reference.

## Basic pyosmium types

::: osmium.BaseHandler
    options:
        heading_level: 3

::: osmium.BaseFilter
    options:
        heading_level: 3

### `HandlerLike` objects

Many functions in pyosmium take handler-like objects as a parameter. Next
to classes that derive from `BaseHandler` and `BaseFilter` you may also
hand in any object that has one of the handler functions `node()`, `way()`,
`relation()`, `area()`, or `changeset()` implemented.
