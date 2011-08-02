from Acquisition import aq_base
from chameleon import compiler, utils
from five.pt.expressions import *
from five.pt.expressions import RestrictionTransform

_marker = object()

from acl import guarded_getattr
RestrictionTransform.secured['_getattr_'] = guarded_getattr


def traverse(cls, base, request, path_items, 
             providedBy = ITraversable.providedBy):
    restricted = cls.restricted

    for name in path_items:
        if providedBy(base):
            base = base.unrestrictedTraverse(name, restricted=restricted)
        else:
            _base = getattr(base, name, _marker)
            if _base is _marker:
                if hasattr(base, '__getitem__'):
                    try:
                        base = base[name]
                        continue
                    except (IndexError, KeyError):
                        pass
            else:
                base = _base
                continue

            base = traversePathElement(
                base, name, (), request=request
                )

    return base

BoboAwareZopeTraverse.traverse = classmethod(traverse)
BoboAwareZopeTraverse.restricted = True
TrustedBoboAwareZopeTraverse.restricted = False


def bt_call(self, base, request, call, *path_items):
    base = self.traverse(base, request, path_items)
    if call and callable(base):
        try:
            return render(base, request)
        except AttributeError, err:
            if err.args[0] != '__call__':
                raise

    return base

def tt_call(self, base, request, call, *path_items):
    base = self.traverse(base, request, path_items)
    if call and callable(base):
        try:
            return base()
        except AttributeError, err:
            if err.args[0] != '__call__':
                raise

    return base

BoboAwareZopeTraverse.__call__ = bt_call
TrustedBoboAwareZopeTraverse.__call__ = tt_call


def load_econtext(name):
    return template("econtext[KEY]", KEY=ast.Str(s=name), mode="eval")

compiler.load_econtext.func_code = load_econtext.func_code

del utils.Scope.__getitem__
