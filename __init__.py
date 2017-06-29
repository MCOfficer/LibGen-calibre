__license__ = 'GPL 3'
__copyright__ = '2017, MCOfficer <mcofficer@gmx.de>'
__docformat__ = 'restructuredtext en'

from calibre.customize import StoreBase

class B_OK_Store(StoreBase):
    name = 'Library Genesis'
    description = 'Access LibGen directly from calibre.'
    author = 'MCOfficer'
    version = (1, 2, 0)
    drm_free_only = True
    actual_plugin = 'calibre_plugins.store_libgen.libgen_plugin:LibGen_Store'
