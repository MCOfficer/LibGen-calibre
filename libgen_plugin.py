__license__ = 'GPL 3'
__copyright__ = '2017, MCOfficer <mcofficer@gmx.de>'
__docformat__ = 'restructuredtext en'


from pylibgen import Library

from PyQt5.Qt import QUrl

from calibre import browser
from calibre.gui2 import open_url
from calibre.gui2.store import StorePlugin
from calibre.gui2.store.basic_config import BasicStoreConfig
from calibre.gui2.store.search_result import SearchResult
from calibre.gui2.store.web_store_dialog import WebStoreDialog


lg = Library()


class LibGen_Store(BasicStoreConfig, StorePlugin):

    def open(self, parent=None, detail_item=None, external=False):
        open_url(QUrl('http://gen.lib.rus.ec'))

    def search(self, query, max_results=10, timeout=60):
        try:
            results = lg.lookup(lg.search(query))
            print('Reached LibGen Mirrors.')
        except Exception as e:
            print(e)
            print('LibGenAPI crashed. In most cases this is caused by unreachable LibGen Mirrors, try again in a few minutes.')
            return

        counter = 0
        br = browser()
        for i in results:
            r = results[counter]
            s = SearchResult()
            s.title = r['title']
            s.author = r['author']
            s.price = '$0.00'
            s.drm = SearchResult.DRM_UNLOCKED
            s.formats = r['extension']
            downloadurl = lg.get_download_url(r['md5'])
            s.downloads[r['extension']] = downloadurl
            yield s
            counter = counter + 1
