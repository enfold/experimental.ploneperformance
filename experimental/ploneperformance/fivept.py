from Acquisition import aq_base
from chameleon import compiler, utils
from five.pt.expressions import *
from five.pt.expressions import RestrictionTransform
from zope.location.interfaces import LocationError

_marker = object()

from acl import guarded_getattr
RestrictionTransform.secured['_getattr_'] = guarded_getattr


def traverse(cls, base, request, path_items, 
             providedBy = ITraversable.providedBy):
    restricted = cls.restricted

    for name in path_items:
        _base = getattr(base, name, _marker)
        if _base is _marker:
            if hasattr(base, '__getitem__'):
                try:
                    base = base[name]
                    continue
                except:
                    pass
        else:
            base = _base
            continue

        if providedBy(base):
            base = base.unrestrictedTraverse(name, restricted=restricted)
        else:
            base = traversePathElement(
                base, name, (), request=request)

    return base

BoboAwareZopeTraverse.traverse = classmethod(traverse)
BoboAwareZopeTraverse.restricted = True
TrustedBoboAwareZopeTraverse.restricted = False

types = {type(None):1, str:1, bool:1, unicode:1, list:1}

def bt_call(self, base, request, call, *path_items):
    tt = type(base)
    stypes = tt in types

    if not path_items:
        if not stypes and call and callable(base):
            return render(base, request)
        return base

    if stypes:
        raise LocationError(base, path_items[0])

    if tt is dict and path_items:
        try:
            base = base[path_items[0]]
            path_items = path_items[1:]
            if not path_items:
                if type(base) not in types and call and callable(base):
                    return render(base, request)
                return base
        except KeyError:
            raise LocationError(base, path_items[0])

    base = self.traverse(base, request, path_items)

    if call and callable(base):
        try:
            return render(base, request)
        except AttributeError, err:
            if err.args[0] != '__call__':
                raise

    return base

def tt_call(self, base, request, call, *path_items):
    tt = type(base)
    stypes = tt in types

    if not path_items:
        if not stypes and call and callable(base):
            try:
                return base()
            except AttributeError, err:
                if err.args[0] != '__call__':
                    raise
        return base

    if stypes:
        raise LocationError(base, path_items[0])

    if tt is dict and path_items:
        try:
            base = base[path_items[0]]
            path_items = path_items[1:]
            if not path_items:
                if type(base) not in types and call and callable(base):
                    try:
                        return base()
                    except AttributeError, err:
                        if err.args[0] != '__call__':
                            raise
                return base
        except KeyError:
            raise LocationError(base, path_items[0])

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


ast = compiler.ast
param = compiler.param

def visit_Module(self, node):
        body = []
            
        body += template("import re")
        body += template("import functools")
        body += template("__marker = object()")
        body += template(
            r"g_re_amp = re.compile(r'&(?!([A-Za-z]+|#[0-9]+);)')"
        )
        body += template(
            r"g_re_needs_escape = re.compile(r'[&<>\"\']').search")

        body += template(
            r"re_whitespace = "
            r"functools.partial(re.compile('\s+').sub, ' ')",
        )

        body += template("_guarded_getattr = getattr")
        
        # Visit module content
        program = self.visit(node.program)

        body += [ast.FunctionDef(
            name=node.name, args=ast.arguments(
                args=[param(b) for b in self._builtins],
                defaults=(),
                ),
            body=program
            )]

        return body

compiler.Compiler.visit_Module = visit_Module
