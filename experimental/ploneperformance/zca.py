from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.component import _api, event
from zope.component import hooks

_api.siteinfo = hooks.siteinfo
_api.getSiteManager = hooks.getSiteManager
event.getSiteManager = hooks.getSiteManager


def __cmp(self, o1, o2):
        if o1 is None:
            return 1
        if o2 is None:
            return -1

        try:
            n1 = o1.__name__, o1.__module__
        except:
            n1 = (getattr(o1, '__name__', ''), getattr(o1,  '__module__', ''))
        n2 = (getattr(o2, '__name__', ''), getattr(o2,  '__module__', ''))

        # This spelling works under Python3, which doesn't have cmp().
        return (n1 > n2) - (n1 < n2)
        
InterfaceClass._InterfaceClass__cmp = __cmp


def getAdapter(object, interface=Interface, name=u'', context=None):
    try:
        return siteinfo.adapter_hook(interface, object, name, default)
    except ComponentLookupError:
        return default

_api.getAdapter.func_code = getAdapter.func_code

def queryAdapter(object, interface=Interface, name=u'', default=None,
                 context=None):
    try:
        return siteinfo.adapter_hook(interface, object, name, default)
    except ComponentLookupError:
        return default

_api.queryAdapter.func_code = queryAdapter.func_code
                                                

def getUtility(interface, name='', context=None):
    utility = getSiteManager(context).queryUtility(interface, name, None)
    if utility is not None:
        return utility
    raise ComponentLookupError(interface, name)
    
_api.getUtility.func_code = getUtility.func_code


def getMultiAdapter(objects, interface=Interface, name=u'', context=None):
    adapter = getSiteManager(context).queryMultiAdapter(objects, interface, name, None)
    if adapter is None:
        raise ComponentLookupError(objects, interface, name)
    return adapter

_api.getMultiAdapter.func_code = getMultiAdapter.func_code


def dispatch(*event):
    getSiteManager().subscribers(event, None)

event.dispatch.func_code = dispatch.func_code


def objectEventNotify(event):
    getSiteManager().subscribers((event.object, event), None)
    
event.objectEventNotify.func_code = objectEventNotify.func_code
