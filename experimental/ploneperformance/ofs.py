"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
# traversable
from OFS.Application import Application
from OFS.interfaces import IApplication
from OFS.Traversable import Traversable

_marker = object()


def getPhysicalPath(self):
    if self._v_PhysicalPath is not None:
        return self._v_PhysicalPath
    try:
        id = self.id or self.__name__
    except:
        id = self.getId()

    path = (id,)

    func = self.getPhysicalPath.im_func

    try:
        p = self.aq_inner.aq_parent
    except:
        p = None

    while p is not None:
        if func is not p.getPhysicalPath.im_func:
                if isinstance(p, Application):
                    path = ('',) + path
                else:
                    path = p.getPhysicalPath() + path
                break
        else:
                try:
                    path = (p.id or p.__name__,) + path
                except:
                    path = (p.getId() or p.__name__,) + path
                try:
                    p = p.aq_parent
                except:
                    p = None

    self._v_PhysicalPath = path
    return path

Traversable._v_PhysicalPath = None
Traversable.getPhysicalPath = getPhysicalPath  

from acl import localData
orig_unrestrictedTraverse = Traversable.unrestrictedTraverse

def unrestrictedTraverse(self, path, default=_marker, restricted=False):
    try:
        cache = localData.cache6
    except AttributeError:
        cache = {}
    
    if type(path) is not str:
        k = (self, tuple(path), restricted)
    else:
        k = (self, path, restricted)

    if k in cache:
        return cache[k]

    res = orig_unrestrictedTraverse(self, path, default, restricted)
    cache[k] = res
    return res

Traversable.unrestrictedTraverse = unrestrictedTraverse


# urllib
always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
_safe_map = {}
for i, c in zip(xrange(256), str(bytearray(xrange(256)))):
    if (i < 128 and c in always_safe):
        _safe_map[c] = c
    else:
        _safe_map[c] = '%%%02X' % ord(c)
_safe_quoters = {}

def quote(s, safe='/+@'):
    if not s:
        if s is None:
            raise TypeError('None object cannot be quoted')
        return s
    cachekey = (safe, always_safe)
    try:
        (quoter, safe) = _safe_quoters[cachekey]
    except KeyError:
        safe_map = _safe_map.copy()
        safe_map.update([(c, c) for c in safe])
        quoter = safe_map.__getitem__
        safe = always_safe + safe
        _safe_quoters[cachekey] = (quoter, safe)
    if not s.rstrip(safe):
        return s
    return ''.join(map(quoter, s))

from OFS import Traversable
from ZPublisher import BaseRequest, HTTPRequest
from Products.SiteAccess import VirtualHostMonster

Traversable.quote = quote
BaseRequest.quote = quote
HTTPRequest.quote = quote
VirtualHostMonster.quote = quote


# BTreeFolder
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base

def BTreeFolder_getattr(self, name):
    try:
        return self._tree[name]
    except KeyError:
        raise AttributeError(name)

def BTreeFolder_getOb(self, id, default=_marker):
    try:
        return self._tree[id].__of__(self)
    except KeyError:
        if default is _marker:
            raise
        else:
            return default

BTreeFolder2Base._getOb = BTreeFolder_getOb
BTreeFolder2Base.__getattr__ = BTreeFolder_getattr
