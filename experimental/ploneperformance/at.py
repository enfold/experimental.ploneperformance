""" """
from Acquisition import aq_base
from Products.Archetypes import Field
from Products.Archetypes.BaseObject import BaseObject


def encode(value, instance, **kwargs):
    """ensure value is an encoded string"""
    if type(value) is unicode:
        return value.encode('utf-8')
    return value
    
Field.encode.func_code = encode.func_code


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
