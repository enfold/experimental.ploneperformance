""" """
# getToolByName
import Products.CMFCore.utils
from zope.component.hooks import getSiteManager

_marker = object()

def getToolByName(obj, name, default=_marker):
    if name in _tool_interface_registry:
        try:
            utility = getSiteManager().getUtility(_tool_interface_registry[name])
            if hasattr(utility, '__of__') and aq_parent(utility) is None:
                utility = utility.__of__(obj)
            return utility
        except ComponentLookupError:
            pass

    try:
        tool = aq_get(obj, name, default, 1)
    except AttributeError:
        if default is _marker:
            raise
        return default
    else:
        if tool is _marker:
            raise AttributeError, name
        return tool

Products.CMFCore.utils.getSiteManager = getSiteManager
Products.CMFCore.utils.getToolByName.func_code = getToolByName.func_code


from Acquisition import aq_parent, aq_base
from Products.CMFCore.TypesTool import TypesTool, ITypeInformation
from Products.CMFCore.ActionInformation import Action, ActionInfo, Message
from Products.CMFCore.utils import _checkPermission


def getInfoData(self):
        category_path = []
        lazy_keys = []
        lazy_map = {}

        lazy_map['id'] = self.id

        parent = aq_parent(self)
        while parent is not None and parent.id != 'portal_actions':
            category_path.append( parent.id )
            parent = aq_parent(parent)
        lazy_map['category'] = '/'.join(category_path[::-1])

        for id, val in self.propertyItems():
            if id[-5:] == '_expr':
                id = id[:-5]
                if val:
                    val = getattr(self, '%s_expr_object' % id)
                    lazy_keys.append(id)
                elif id == 'available':
                    val = True
            elif id == 'i18n_domain':
                continue
            elif id == 'link_target':
                val = val or None
            elif self.i18n_domain and id in ('title', 'description'):
                val = Message(val, self.i18n_domain)
            lazy_map[id] = val

        return (lazy_map, lazy_keys)
        
Action.getInfoData = getInfoData


def checkPermissions(self, ec):
        """ Check permissions in the current context.
        """
        category = self['category']
        object = ec.contexts['object']
        if object is not None and \
            category[:6] in ('object', 'workfl', 'docume'):
            context = object
        else:
            folder = ec.contexts['folder']
            if folder is not None and category[:6] == 'folder':
                context = folder
            else:
                context = ec.contexts['portal']

        for permission in self._permissions:
            if _checkPermission(permission, context):
                return True
        return False

ActionInfo._checkPermissions = checkPermissions


def listTypeInfo( self, container=None ):
        rval = []
        for t in self.objectValues():
            #if ITypeInformation.providedBy(t):
            rval.append(t)
        rval = [t for t in rval if t.id]
        if container is not None:
            rval = [t for t in rval if t.isConstructionAllowed(container)]
        return rval

def listContentTypes(self, container=None, by_metatype=0):
        typenames = {}
        for t in self.listTypeInfo( container ):
            name = t.id
            typenames[ name ] = None

        result = typenames.keys()
        result.sort()
        return result

def getTypeInfo( self, contentType ):
        if hasattr(aq_base(contentType), 'getPortalTypeName'):
            contentType = contentType.getPortalTypeName()
            if contentType is None:
                return None
        try:
            ob = getattr( self, contentType, None )
        except:
            return

        return ob


TypesTool.listTypeInfo = listTypeInfo
TypesTool.listContentTypes = listContentTypes
TypesTool.getTypeInfo = getTypeInfo
