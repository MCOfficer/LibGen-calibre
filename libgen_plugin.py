__license__ = 'GPL 3'
__copyright__ = '2017, MCOfficer <mcofficer@gmx.de>'
__docformat__ = 'restructuredtext en'


from pylibgen import Library

from contextlib import closing

from PyQt5.Qt import QUrl

from calibre import browser
from calibre.gui2 import open_url
from calibre.gui2.store import StorePlugin
from calibre.gui2.store.basic_config import BasicStoreConfig
from calibre.gui2.store.search_result import SearchResult
from calibre.gui2.store.web_store_dialog import WebStoreDialog


lg = Library()
br = browser()


class LibGen_Store(BasicStoreConfig, StorePlugin):


    RES_THRESH = 5

    def open(self, parent=None, detail_item=None, external=False):
        open_url(QUrl('http://gen.lib.rus.ec'))

    def get_cover_url(self, md5):
        try:
            coverpage = 'http://libgen.io/book/index.php?md5=' + md5
            coverpage = coverpage.replace('ads.', 'book/index.')
            with closing(br.open(coverpage, timeout=10)) as f:
                doc = f.read()
            cover = doc[doc.find('/covers'):doc.find('.jpg') + 4]
            return 'http://libgen.io' + cover
        except Exception as e:
            print("Failed to find cover url for book with md5 " + md5)
            return ""

    def search(self, query, max_results=10, timeout=60):
        try:
            results = lg.lookup(lg.search(query))
            print('Reached LibGen Mirrors.')
        except Exception as e:
            print(e)
            print('pylibgen crashed. In most cases this is caused by unreachable LibGen Mirrors, try again in a few minutes.')
            return

        self.num_results = len(results)

        for r in results:
            s = SearchResult()
            s.title = r['title']
            s.author = r['author']
            s.price = '$0.00'
            s.drm = SearchResult.DRM_UNLOCKED
            s.formats = r['extension']
            s.detail_item = r['md5']
            yield s

    def get_details(self, search_result, timeout=60):
        if self.num_results > self.RES_THRESH:
            return False
        s = search_result
        s.cover_url = self.get_cover_url(s.detail_item)
        s.downloads[s.formats] = lg.get_download_url(s.detail_item)
        return True
