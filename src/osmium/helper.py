from osmium._osmium import SimpleHandler

def make_simple_handler(node=None, way=None, relation=None, area=None):
    """ Convenience function that creates a `SimpleHandler` from a set of
        callback functions. Each of the parameters takes an optional callable
        that must expect a single positional parameter with the object being
        processed.
    """
    class __HandlerWithCallbacks(SimpleHandler):
        pass

    if node is not None:
        __HandlerWithCallbacks.node = staticmethod(node)
    if way is not None:
        __HandlerWithCallbacks.way = staticmethod(way)
    if relation is not None:
        __HandlerWithCallbacks.relation = staticmethod(relation)
    if area is not None:
        __HandlerWithCallbacks.area = staticmethod(area)

    return __HandlerWithCallbacks()
