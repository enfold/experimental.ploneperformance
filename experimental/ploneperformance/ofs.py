"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
# traversable
from OFS.Application import Application
from OFS.interfaces import IApplication
from OFS.Traversable import Traversable
from OFS import Traversable as modTraversable
from acl import localData


def getPhysicalPath(self, _id = id):
    try:
        id = self.id or self.__name__
    except:
        id = self.getId()

    try:
        cache = localData.cache2
    except AttributeError:
        cache = {}

    k = (1, id, _id(self))
    if k in cache:
        return cache[k]


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

    cache[k] = path
    return path

Traversable.getPhysicalPath = getPhysicalPath  

#orig_restrictedTraverse = Traversable.restrictedTraverse
#orig_unrestrictedTraverse = Traversable.unrestrictedTraverse

def unrestrictedTraverse(self, path, default=modTraversable._marker, restricted=False):
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

def restrictedTraverse(self, path, default=modTraversable._marker):
    return unrestrictedTraverse(self, path, default, True)

#Traversable.restrictedTraverse = restrictedTraverse
#Traversable.unrestrictedTraverse = unrestrictedTraverse


orig_absolute_url = Traversable.absolute_url

def absolute_url(self, relative=0, _id=id):
    """ """
    try:
        cache = localData.cache2
    except AttributeError:
        cache = {}

    try:
        id = self.id or self.__name__
    except:
        id = self.getId()

    k = (2, _id(self), id, relative)
    if k in cache:
        return cache[k]
    
    url = orig_absolute_url(self, relative)
    cache[k] = url
    return url

Traversable.absolute_url = absolute_url


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

_marker = object()

def BTreeFolder_getattr(self, name):
    try:
        return self._tree[name]
    except KeyError:
        raise AttributeError(name)

#BTreeFolder2Base.__getattr__ = BTreeFolder_getattr
