from zope.publisher import skinnable

def setDefaultSkin(request):
    pass
    
skinnable.setDefaultSkin.func_code = setDefaultSkin.func_code
