"""Security management"""
from threading import local
from AccessControl import ImplC
from AccessControl import ZopeGuards
from AccessControl import SecurityManagement
from AccessControl import ZopeSecurityPolicy
from AccessControl.ImplC import SecurityManager
from AccessControl.cAccessControl import guarded_getattr as c_guarded_getattr
from OFS import Traversable


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
    localData.cache6 = {}

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
