""" """
from zope.component import queryUtility
from Acquisition import aq_base
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import Field
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.BaseObject import BaseObject
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
        print 'miss'
        cache = {}
    k = mode, instance
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
    
BaseObject.getCharset = getCharset

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
        #target = queryMultiAdapter((self, REQUEST), Interface, name)
        if target is not None:
            target = None
        else:
            target = getattr(self, name, None)

        if target is not None:
            return target
        else:
            raise AttributeError(name)

BaseObject.__bobo_traverse__ = bobo_traverse


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
