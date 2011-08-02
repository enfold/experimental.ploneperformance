"""Security management"""
from threading import local
from AccessControl import ImplC
from AccessControl import ZopeGuards
from AccessControl import SecurityManagement
from AccessControl import ZopeSecurityPolicy
from AccessControl.ImplC import SecurityManager
from AccessControl.cAccessControl import guarded_getattr as c_guarded_getattr


def getSecurityManager():
    """Get a security manager, for the current thread.
    """
    try:
        return _managers_local.sm
    except AttributeError:
        pass
        
    nobody = getattr(SpecialUsers, 'nobody', None)
    if nobody is None:
        # Initialize SpecialUsers by importing User.py.
        import User
        nobody = SpecialUsers.nobody
    return newSecurityManager(None, nobody)


def setSecurityManager(manager):
    """install *manager* as current security manager for this thread."""
    thread_id=get_ident()
    _managers[thread_id]=manager
    _managers_local.sm = manager



def newSecurityManager(request, user):
    """Set up a new security context for a request for a user
    """
    thread_id=get_ident()
    sm=SecurityManager(
        thread_id,
        SecurityContext(user),
        )
    _managers[thread_id] = sm
    _managers_local.sm = sm
    return sm


def noSecurityManager():
    try: 
        del _managers[get_ident()]
        del _managers_local.sm
    except: pass


SecurityManagement._managers_local = local()
SecurityManagement.getSecurityManager.func_code = getSecurityManager.func_code
SecurityManagement.setSecurityManager.func_code  = setSecurityManager.func_code 
SecurityManagement.noSecurityManager.func_code = noSecurityManager.func_code
SecurityManagement.newSecurityManager.func_code = newSecurityManager.func_code



def init(self, ident, context):
    super(SecurityManager, self).__init__(ident, context)

    localData.cache = {}
    localData.cache2 = {}
    localData.cache3 = {}
    localData.cache4 = {}
    localData.cache5 = {}

def checkPermission(self, permission, object):
    k = (permission, object)
    cache = localData.cache
    if k in cache:
        return cache[k]

    res = super(SecurityManager, self).checkPermission(permission, object)
    cache[k] = res
    return res


localData = local()
SecurityManager.__init__ = init
SecurityManager.checkPermission = checkPermission

_marker = object()
def guarded_getattr(inst, name, default=_marker):
    cache = localData.cache5

    k = (id(inst), name)
    if k in cache:
       return cache[k]

    res = c_guarded_getattr(inst, name, default)
    cache[k] = res
    return res

from five.pt.expressions import RestrictionTransform
RestrictionTransform.secured['_getattr_'] = guarded_getattr


def getRoles(container, name, value, default):
    global _localData
    try:
        cache = _localData.cache2
    except AttributeError:
        cache = {}
        _localData.cache2 = cache

    k = (name,)
    if type(container) is MethodType:
        k = k + (container.im_self,)
    else:
        print type(container)
        k = k + (container,)
    if type(value) is MethodType:
        k = k + (value.im_self,)
    else:
        print type(value)
        k = k + (value,)
    if k in cache:
        return cache[k]
    print k

    
    global rolesForPermissionOn  # XXX:  avoid import loop

    if rolesForPermissionOn is None:
        from PermissionRole import rolesForPermissionOn

    roles = getattr(value, '__roles__', _noroles)
    if roles is _noroles:
        if not name or not isinstance(name, basestring):
            return default

        if type(value) is MethodType:
            container = value.im_self

        cls = getattr(container, '__class__', None)
        if cls is None:
            cache[k] = default
            return default
        
        roles = getattr(cls, name+'__roles__', _noroles)
        if roles is _noroles:
            cache[k] = default
            return default

        value = container

    if roles is None or isinstance(roles, tuple_or_list):
        cache[k] = roles
        return roles
    
    rolesForPermissionOn = getattr(roles, 'rolesForPermissionOn', None)
    if rolesForPermissionOn is not None:
        roles = rolesForPermissionOn(value)

    cache[k] = roles
    return roles


#ZopeSecurityPolicy._localData = localData
#ZopeSecurityPolicy.getRoles.func_code = getRoles.func_code
