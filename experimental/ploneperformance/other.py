"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
# skip makestr
from Products.PluggableAuthService import utils

def createViewName(method_name, user_handle=None):
    if not user_handle:
        return method_name
    else:
        return '%s-%s' % (method_name, user_handle)

def createKeywords(**kw):
    keywords = sha()

    items = kw.items()
    items.sort()
    for k, v in items:
        keywords.update(k)
        keywords.update(str(v))

    return {'keywords': keywords.hexdigest()}

utils.createViewName.func_code = createViewName.func_code
utils.createKeywords.func_code = createKeywords.func_code


# getToolByName
import Products.CMFCore.utils
from zope.component import getSiteManager
from zope.component.interfaces import ComponentLookupError
from Acquisition import aq_get, aq_parent
from Acquisition.interfaces import IAcquirer
from Products.CMFCore.utils import _tool_interface_registry

_marker = object()


def getToolByName(obj, name, default=_marker):
    request = getattr(obj, 'REQUEST', None)
    cache = getattr(request, '_gtbn_cache', {})
    if name in cache:
        return cache[name]

    tool_interface = _tool_interface_registry.get(name)

    tool = None

    if tool_interface is not None:
        try:
            utility = getSiteManager().getUtility(tool_interface)
            # Site managers, except for five.localsitemanager, return unwrapped
            # utilities. If the result is something which is acquisition-unaware
            # but unwrapped we wrap it on the context.
            if IAcquirer.providedBy(obj) and \
                    aq_parent(utility) is None and \
                    IAcquirer.providedBy(utility):
                utility = utility.__of__(obj)
            tool = utility
        except ComponentLookupError:
            # behave in backwards-compatible way
            # fall through to old implementation
            pass
    
    if tool is None:
        try:
            tool = aq_get(obj, name, default, 1)
        except AttributeError:
            if default is _marker:
                raise
            tool = default
        else:
            if tool is _marker:
                raise AttributeError, name

    cache[name] = tool
    try:
        setattr(request, '_gtbn_cache', cache)
    except:
        pass
    return tool

Products.CMFCore.utils.getSiteManager = getSiteManager
Products.CMFCore.utils.getToolByName.func_code = getToolByName.func_code


# Interface.__eq__ optimization
from Persistence import PersistentMapping
from Acquisition import aq_parent, aq_inner
from Products.PluginRegistry.PluginRegistry import PluginRegistry

def getPlugins(self, plugin_type):
    parent = aq_parent(aq_inner(self))

    try:
        return self._plugins.setdefault(plugin_type, ())
    except:
        self._plugins = PersistentMapping()
        return self._plugins.setdefault(plugin_type, ())

PluginRegistry._getPlugins = getPlugins
