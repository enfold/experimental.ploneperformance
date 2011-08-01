from zope.publisher import skinnable
from zope.component import provideAdapter
from zope.annotation.interfaces import IAnnotations
from ZPublisher.HTTPRequest import HTTPRequest

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

HTTPRequest.taintWrapper = taintWrapper
HTTPRequest.setVirtualRoot = setVirtualRoot
HTTPRequest.physicalPathToVirtualPath = physicalPathToVirtualPath