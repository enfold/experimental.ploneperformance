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


# Interface.__eq__ optimization
from Persistence import PersistentMapping
from Acquisition import aq_parent, aq_inner
from Products.PluginRegistry.PluginRegistry import PluginRegistry, logger, _satisfies

def getPlugins(self, plugin_type):
    parent = aq_parent(aq_inner(self))

    try:
        return self._plugins.setdefault(plugin_type, ())
    except:
        self._plugins = PersistentMapping()
        return self._plugins.setdefault(plugin_type, ())

PluginRegistry._getPlugins = getPlugins


def listPlugins(self, plugin_type):
        if self._v_cache is None:
            self._v_cache = {}

        if plugin_type in self._v_cache:
            return self._v_cache[plugin_type]

        result = []
        parent = aq_parent(aq_inner(self))

        for plugin_id in self._getPlugins(plugin_type):
            plugin = parent._getOb(plugin_id)
            if not _satisfies(plugin, plugin_type):
                logger.debug('Active plugin %s no longer implements %s'
                                % (plugin_id, plugin_type)
                           )
            else:
                result.append((plugin_id, plugin))

        self._v_cache[plugin_type] = result
        return result


PluginRegistry._v_cache = None
PluginRegistry.listPlugins = listPlugins
