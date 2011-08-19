""" """
from zope.component import queryUtility
from zope.i18nmessageid import Message
from ZPublisher.interfaces import UseTraversalDefault
from Acquisition import aq_base
from Acquisition import ImplicitAcquisitionWrapper
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import Field
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.BaseObject import \
    _marker, BaseObject, ISchema, getSchemata, mapply
from Products.Archetypes.ExtensibleMetadata import _, ExtensibleMetadata
try:
    from plone.i18n.locales.interfaces import IMetadataLanguageAvailability
    HAS_PLONE_I18N = True
except ImportError:
    HAS_PLONE_I18N = False


from acl import localData


def encode(value, instance, **kwargs):
    """ensure value is an encoded string"""
    if type(value) is unicode:
        return value.encode('utf-8')
    return value
    
Field.encode.func_code = encode.func_code


def checkPermission(self, mode, instance):
    """ """
    try:
        cache = localData.cache4
    except AttributeError:
        cache = {}
    k = mode, instance._p_oid
    if k in cache:
        return cache[k]
        
    if mode in ('w', 'write', 'edit', 'set'):
        perm = self.write_permission
    elif mode in ('r', 'read', 'view', 'get'):
        perm = self.read_permission
    else:
        cache[k] = None
        return None
    res = getSecurityManager().checkPermission( perm, instance )
    cache[k] = res
    return res

Field.Field.checkPermission = checkPermission


def getCharset(self):
    """ """
    return 'utf-8'

def Schemata(self):
    """Returns the Schemata for the Object.
    """
    try:
        if self._v_cache_schemata is not None:
            return self._v_cache_schemata
    except:
        pass

    s = getSchemata(self)
    self._v_cache_schemata = s
    return s

def Schema(self):
    """Return a (wrapped) schema instance for this object instance.
    """
    try:
        if self._v_cache_schema is not None:
            return self._v_cache_schema
    except:
        pass

    res = ImplicitAcquisitionWrapper(ISchema(self), self)
    self._v_cache_schema = res
    return res

    
BaseObject._v_cache_schema = None
BaseObject._v_cache_schemata = None
BaseObject.getCharset = getCharset
BaseObject.Schemata = Schemata
BaseObject.Schema = Schema


from zope.component import getSiteManager
from zope.interface import Interface, providedBy
from zope.component import queryMultiAdapter

def bobo_traverse(self, REQUEST, name):
    """ """
    data = self.getSubObject(name, REQUEST)
    if data is not None:
        return data

    if hasattr(aq_base(self), name):
       return getattr(self, name)
    else:
        sm = getSiteManager()
        target = sm.adapters.lookup(
            (providedBy(self), providedBy(REQUEST)), Interface, name, None)
        if target is not None:
            target = None
        else:
            target = getattr(self, name, None)

        if target is not None:
            return target
        else:
            raise AttributeError(name)

#BaseObject.__bobo_traverse__ = bobo_traverse


def bo_getitem(self, key, default=_marker):
    """Overloads the object's item access."""
    schema = self.Schema()
    keys = schema.keys()

    if key not in keys:
        value = getattr(aq_base(self), key, default)
        if value is default:
            raise KeyError, key
        else:
            return value

    field = schema[key]
    accessor = field.getEditAccessor(self)
    if not accessor:
        accessor = field.getAccessor(self)

    kw = {'raw':1, 'field': field.__name__}
    value = mapply(accessor, **kw)
    return value

BaseObject.__getitem__ = bo_getitem


def languages(self):
        """ ~2200 function calls """
        util = None

        use_combined = False
        # Respect the combined language code setting from PloneLanguageTool
        lt = getToolByName(self, 'portal_languages', None)
        if lt is not None:
            use_combined = lt.use_combined_language_codes

        cache = getattr(lt, '_v_at_extensible_md_languages', None)
        if cache is not None:
            return cache

        # Try the utility first
        if HAS_PLONE_I18N:
            util = queryUtility(IMetadataLanguageAvailability)
        # Fall back to acquiring availableLanguages
        if util is None:
            languages = getattr(self, 'availableLanguages', None)
            if callable(languages):
                languages = languages()
            # Fall back to static definition
            if languages is None:
                return DisplayList(
                    (('en','English'), ('fr','French'), ('es','Spanish'),
                     ('pt','Portuguese'), ('ru','Russian')))
        else:
            languages = util.getLanguageListing(combined=use_combined)
            languages.sort(key=lambda x:x[1])
            # Put language neutral at the top.
            languages.insert(0,(u'',_(u'Language neutral')))

        dl = DisplayList(languages)
        lt._v_at_extensible_md_languages = dl
        return dl

ExtensibleMetadata.languages = languages


# schemata
from Products.Archetypes import Schema

def addField(self, field):
    field = aq_base(field)
    name = field.__name__
    if name not in self._names:
        self._names.append(name)
    self._fields[name] = field

Schema.Schemata.addField = addField


from Products.Archetypes.utils import Vocabulary

def getValue(self, key, default=None):
    """ """
    v = self._keys.get(key, None)
    value = default
    if v:
            value = v[1]
    else:
            for k, v in self._keys.items():
                if repr(key) == repr(k):
                    value = v[1]
                    break

    if self._i18n_domain and self._instance:
            msg = self._i18n_msgids.get(key, None) or value
        
            if isinstance(msg, Message):
                return msg
        
            if not msg:
                return ''
          
            return translate(msg, self._i18n_domain,
                             context=self._instance.REQUEST, default=value)
    else:
            return value


Vocabulary.getValue = getValue
