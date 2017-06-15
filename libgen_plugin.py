__license__ = 'GPL 3'
__copyright__ = '2017, MCOfficer <mcofficer@gmx.de>'
__docformat__ = 'restructuredtext en'

import urllib2
from contextlib import closing

import libgenapi

from PyQt5.Qt import QUrl

from calibre import browser
from calibre.gui2 import open_url
from calibre.gui2.store import StorePlugin
from calibre.gui2.store.basic_config import BasicStoreConfig
from calibre.gui2.store.search_result import SearchResult
from calibre.gui2.store.web_store_dialog import WebStoreDialog

class LibGen_Store(BasicStoreConfig, StorePlugin):

    def open(self, parent=None, detail_item=None, external=False):
        open_url(QUrl('http://gen.lib.rus.ec'))

    def search(self, query, max_results=10, timeout=60):

        lg=libgenapi.Libgenapi(["http://libgen.io","http://libgen.in","http://libgen.org","http://gen.lib.rus.ec"])
        results = lg.search(query)

        counter = 0

        for i in results:
            r = results[counter]

            s = SearchResult()
            s.title = r['title']
            s.author = r['author']
            s.price = '$0.00'
            s.drm = SearchResult.DRM_UNLOCKED
            extension = r['extension']

            #prep download via libgen
            lpwview = 'http://libgen.io' + r['mirrors'][1]
            br = browser()
            with closing(br.open(lpwview, timeout=10)) as f:
                doc = f.read()
            linkpos = doc.find('/get.php?md5=') -19
            linkend = doc.find("'><h2>DOWNLOAD")
            downloadurl = doc[linkpos:linkend]
            s.downloads[extension.upper() + ' (via libgen)'] = downloadurl


            s.formats = extension
            yield s
            counter = counter + 1
