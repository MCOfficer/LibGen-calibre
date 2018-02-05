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
    url = 'http://gen.lib.rus.ec'

    def open(self, parent=None, detail_item=None, external=False):

        detail_url = None
        if detail_item:
            detail_url = self.get_cover_page(detail_item)

        if external or self.config.get('open_external', False):
            open_url(QUrl(detail_url if detail_url else self.url))
        else:
            d = WebStoreDialog(self.gui, self.url, parent, detail_url)
            d.setWindowTitle(self.name)
            d.set_tags(self.config.get('tags', ''))
            d.exec_()

    def get_cover_url(self, md5):
        try:
            coverpage = self.get_cover_page(md5)
            with closing(br.open(coverpage, timeout=10)) as f:
                doc = f.read()
            cover = doc[doc.find('/covers'):doc.find('.jpg') + 4]
            return self.url + cover
        except Exception as e:
            print("Failed to find cover url for book with md5 " + md5)
            return ""

    def get_cover_page(self, md5):
        coverpage = "%s/book/index.php?md5=%s" % (self.url, md5)
        return coverpage.replace('ads.', 'book/index.')


    def search(self, query, max_results=10, timeout=60):
        try:
            results = lg.lookup(lg.search(query, 'title') + lg.search(query, 'author'))
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
