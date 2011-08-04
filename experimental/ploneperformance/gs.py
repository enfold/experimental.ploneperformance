from Products.GenericSetup.tool import *
from Products.GenericSetup.tool import SetupTool

from acl import localData

def clear():
    localData.cache.clear()
    localData.cache2.clear()
    localData.cache3.clear()
    localData.cache4.clear()
    localData.cache5.clear()
    localData.cache6.clear()


def _doRunImportStep(self, step_id, context):
        """ Run a single import step, using a pre-built context.
        """
        clear()
        __traceback_info__ = step_id
        marker = object()
    
        handler = self.getImportStep(step_id)
    
        if handler is marker:
            raise ValueError('Invalid import step: %s' % step_id)
    
        if handler is None:
            msg = 'Step %s has an invalid import handler' % step_id
            logger = logging.getLogger('GenericSetup')
            logger.error(msg)
            return 'ERROR: ' + msg

        return handler(context)


SetupTool._doRunImportStep = _doRunImportStep