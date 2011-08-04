from zope import interface
from zope.publisher import skinnable
from zope.component import provideAdapter
from zope.annotation.interfaces import IAnnotations
from ZPublisher.HTTPRequest import HTTPRequest
from Products.CMFDefault.interfaces import ICMFDefaultSkin
from ofs import quote

interface.classImplements(HTTPRequest, ICMFDefaultSkin)

def setDefaultSkin(request):
    pass

skinnable.setDefaultSkin.func_code = setDefaultSkin.func_code

def getAnnotations(request):
    if '__annotations__' in request.__dict__:
        return request.__dict__['__annotations__']

    annotations = {}
    request.__dict__['__annotations__'] = annotations

    return annotations

provideAdapter(getAnnotations, (HTTPRequest,), IAnnotations)


from zope.traversing import namespace

def nsParse(name):
    ns = ''
    p = name[:2]
    if p == '@@':
        ns = 'view'
        name = name[2:]
    elif p == '++':
        match = namespace_pattern.match(name)
        if match:
            prefix, ns = match.group(0, 1)
            name = name[len(prefix):]

    return ns, name

namespace.nsParse.func_code = nsParse.func_code


def setVirtualRoot(self, path, hard=0):
    """ Treat the current publishing object as a VirtualRoot """
    other = self.other
    if isinstance(path, basestring):
        path = path.split('/')
    self._script[:] = map(quote, filter(None, path))
    del self._steps[:]
    parents = other['PARENTS']
    if hard:
        del parents[:-1]
    other['VirtualRootPhysicalPath'] = parents[-1].getPhysicalPath()
    other['VirtualRootPhysicalPathLen'] = len(other['VirtualRootPhysicalPath'])
    self._resetURLS()

def physicalPathToVirtualPath(self, path):
    """ Remove the path to the VirtualRoot from a physical path """
    if isinstance(path, basestring):
        path = path.split( '/')
    rpp = self.other.get('VirtualRootPhysicalPath', ('',))
    rpplen = self.other.get('VirtualRootPhysicalPathLen', 1)
    return path[rpplen:]

def taintWrapper(self, enabled=False):
    return self

def conform(self, iface):
    if iface is IAnnotations:
        try:
            return self.__dict__['__annotations__']
        except:
            annotations = {}
            self.__dict__['__annotations__'] = annotations
            return annotations

    return iface.__adapt__(self)

def nonzero(self):
    return True

def physicalPathToURL(self, path, relative=0):
    """ Convert a physical path into a URL in the current context """
    path = self._script + [quote(s) for s in self.physicalPathToVirtualPath(path)]
    if relative:
        path.insert(0, '')
    else:
        try:
            path.insert(0, self.other['SERVER_URL'])
        except:
            path.insert(0, self['SERVER_URL'])
    return '/'.join(path)

orig_init = HTTPRequest.__init__

def init(self, stdin, environ, response, clean=0):
    orig_init(self, stdin, environ, response, clean=0)
    self.debug = self._debug
    self.RESPONSE = self.response


HTTPRequest.__init__ = init
HTTPRequest.__conform__ = conform
HTTPRequest.__nonzero__ = nonzero
HTTPRequest.taintWrapper = taintWrapper
HTTPRequest.setVirtualRoot = setVirtualRoot
HTTPRequest.physicalPathToURL = physicalPathToURL
HTTPRequest.physicalPathToVirtualPath = physicalPathToVirtualPath
