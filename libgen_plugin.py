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

        lg=libgenapi.Libgenapi(["http://libgen.io","http://libgen.in","http://libgen.org","http://gen.lib.rus.ec","http://libgen.pw"])
        results = lg.search(query)

        counter = 0

        for i in results:
            if '}, {' in results: #if results is a tuple
                r = results[counter]
            else: #if results is a dictionary (only one hit)
                r = results

            s = SearchResult()
            s.title = r['title']
            s.author = r['author']
            s.price = '$0.00'
            s.drm = SearchResult.DRM_UNLOCKED
            extension = r['extension']

            #prep download via libgen.pw
            lpwview = r['mirrors'][0]
            br = browser()
            with closing(br.open(lpwview, timeout=10)) as f:
                doc = f.read()
            locationpos = doc.find('<td class="type3">location</td>') + 56
            location = doc[locationpos:locationpos+26]
            key = location[:5]
            md5 = location[7:]
            hidden0 = s.author + ' ' + s.title
            hidden0 = urllib2.quote(hidden0.replace(' ', '+'))
            hidden0 = hidden0.replace('%2B', '+')
            downloadurl = 'https://libgen.pw/noleech1.php?hidden=' + key + '%2F' + md5 + '&hidden0=' + hidden0 + '.' + extension

            s.downloads[extension.upper()] = downloadurl
            s.formats = extension

            yield s
            counter = counter + 1
