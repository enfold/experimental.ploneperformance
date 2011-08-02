""" /Plone/front-page/edit
  reduce number of function calls by ~13000 
"""

import simplejson

from Products.TinyMCE import utility
from Products.TinyMCE.adapters import \
  JSONFolderListing, JSONDetails, JSONSearch
  
utility.json = simplejson
JSONFolderListing.json = simplejson
JSONDetails.json = simplejson
JSONSearch.json = simplejson
