# Patch the Zope3 negotiator to cache the negotiated languages
from gettext import GNUTranslations
from Products.PlacelessTranslationService.memoize import memoize_second
from Products.PlacelessTranslationService.lazycatalog import LazyGettextMessageCatalog
from zope.i18n.gettextmessagecatalog import _KeyErrorRaisingFallback
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.negotiator import Negotiator
from zope.i18n.negotiator import normalize_langs
from zope.cachedescriptors.property import Lazy

TEMPLATE_LANGUAGE = ('en',)

_cache = {}
_bcache = {}

def getLanguage(self, langs, env):
    envadapter = IUserPreferredLanguages(env)
    userlangs = envadapter.getPreferredLanguages()
    # Always add the template language to the available ones. This allows the
    # template language to be picked without the need for a message catalog
    # for every domain for it to be registered.
    langs = tuple(langs) + TEMPLATE_LANGUAGE
    
    global _cache, _bcache
    l_cache = _cache
    b_cache = _bcache

    notnormalized = [l for l in langs if l not in b_cache]
    if notnormalized:
        l_cache.update(normalize_langs(notnormalized))
        b_cache.update(dict((v, k) for k, v in l_cache.items()))
    
      
    # Prioritize on the user preferred languages.  Return the
    # first user preferred language that the object has available.
    #langs = normalize_langs(langs)
    for lang in userlangs:
        if lang in l_cache:
            return l_cache[lang]
        # If the user asked for a specific variation, but we don't
        # have it available we may serve the most generic one,
        # according to the spec (eg: user asks for ('en-us',
        # 'de'), but we don't have 'en-us', then 'en' is preferred
        # to 'de').
        parts = lang.split('-')
        if len(parts) > 1 and parts[0] in l_cache:
            return l_cache.get(parts[0])
    return None

Negotiator.getLanguage = memoize_second(getLanguage)


def __init__(self, language, domain, path_to_file):
    """Initialize the message catalog"""
    self.language = language
    self.domain = domain
    self._path_to_file = path_to_file

def _catalog(self):
    'See IMessageCatalog'
    fp = open(self._path_to_file, 'rb')
    try:
        catalog = GNUTranslations(fp)
        catalog.add_fallback(_KeyErrorRaisingFallback())
        return catalog
    finally:
        fp.close()

LazyGettextMessageCatalog.__init__ = __init__
LazyGettextMessageCatalog._catalog = Lazy(_catalog)
del LazyGettextMessageCatalog.getMessage
del LazyGettextMessageCatalog.queryMessage
