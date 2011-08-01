"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
# placeless control panel
from ComputedAttribute import ComputedAttribute
from App.Product import ProductFolder
from App.ApplicationManager import ApplicationManager
from OFS import Folder
from OFS import Application as AppMOD
from OFS.userfolder import UserFolder
from OFS.Application import Application, AppInitializer

APP_MANAGER = None


def Control_Panel(self):
    return APP_MANAGER.__of__(self)

Application.Control_Panel = Control_Panel
Application.Control_Panel = ComputedAttribute(Application.Control_Panel)
Application.manage_options=((
        Folder.Folder.manage_options[0],
        Folder.Folder.manage_options[1],
        {'label': 'Control Panel', 'action': 'Control_Panel/manage_main'}, ) +
                            Folder.Folder.manage_options[2:]
                            )


def install_cp_and_products(self):
    global APP_MANAGER
    APP_MANAGER = ApplicationManager()
    APP_MANAGER.Products=ProductFolder()

    app = self.getApp()
    app._p_activate()

    # Remove Control Panel.
    if 'Control_Panel' in app.__dict__.keys():
        del app.__dict__['Control_Panel']
        app._objects = tuple(i for i in app._objects
                                 if i['id'] != 'Control_Panel')
        self.commit('Removed persistent Control_Panel')


AppInitializer.install_cp_and_products = install_cp_and_products


def Application__init(self):
    # Initialize users
    uf = UserFolder()
    self.__allow_groups__ = uf
    self._setObject('acl_users', uf)


Application.__init__ = Application__init


# no session, no errorlog
def _empty(self):
    pass

#AppInitializer.install_errorlog = _empty
#AppInitializer.install_tempfolder_and_sdc = _empty
#AppInitializer.install_session_data_manager = _empty
#AppInitializer.install_browser_id_manager = _empty
