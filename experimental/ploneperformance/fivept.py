from five.pt.expressions import *

_marker = object()


def traverse(cls, base, request, path_items):

        method = cls.traverse_method
        for name in path_items:
                traverser = getattr(base, method, None)
                if traverser is not None:
                    base = traverser(name)
                else:
                    _base = getattr(base, name, _marker)
                    if _base is _marker and hasattr(base, '__getitem__'):
                        try:
                            _base = base[name]
                        except IndexError, KeyError:
                            pass
                    if _base is _marker:
                        base = traversePathElement(
                            base, name, (), request=request
                            )
                    else:
                        base = _base

        return base

BoboAwareZopeTraverse.traverse = classmethod(traverse)
