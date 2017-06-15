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

        lg=libgenapi.Libgenapi(["http://libgen.io","http://gen.lib.rus.ec","http://libgen.in","http://libgen.org"])
        try:
            results = lg.search(query)
            abort = False
            print 'Reached LibGen Mirrors.'
        except:
            print 'LibGenAPI crashed. In most cases this is caused by unreachable LibGen Mirrors, try again in a few minutes.'
            raise
            abort = True

        counter = 0
        br = browser()
        if not abort:
            for i in results:
                r = results[counter]

                s = SearchResult()
                s.title = r['title']
                s.author = r['author']
                s.price = '$0.00'
                s.drm = SearchResult.DRM_UNLOCKED
                extension = r['extension']

                #prep cover
                coverpage = 'http://gen.lib.rus.ec' + r['mirrors'][1]
                coverpage = coverpage.replace('ads.', 'book/index.')
                with closing(br.open(coverpage, timeout=10)) as f:
                    doc = f.read()
                linkpos = doc.find('/covers')
                linkend = doc.find('.jpg') + 4
                cover = doc[linkpos:linkend]
                s.cover_url = cover

                #prep download via libgen
                lgpage = 'http://libgen.io' + r['mirrors'][1]
                with closing(br.open(lgpage, timeout=10)) as f:
                    doc = f.read()
                linkend = doc.find('><h2>DOWNLOAD') - 1
                doc = doc[linkend-100:linkend]
                linkpos = doc.find('http')
                libgendl = doc[linkpos:linkend]
                libgendl = libgendl.replace('amp;', '')
                print libgendl
                s.downloads[extension + ' (via libgen)'] = libgendl

                #prep download via b-ok/booksc/bookzz
                bokpage = r['mirrors'][2]
                with closing(br.open(bokpage, timeout=10)) as f:
                    doc = f.read()
                pos = doc.find('/dl/')
                doc = doc[pos-30:pos+30]
                linkend = doc.find(' title=') - 1
                linkpos = doc.find('http')
                bokdl = doc[linkpos:linkend]
                print bokdl
                s.downloads[extension + ' (via b-ok)'] = bokdl

                #prep download via bookfi
                bfpage = r['mirrors'][3]
                with closing(br.open(bfpage, timeout=10)) as f:
                    doc = f.read()
                pos = doc.find('/dl/')
                doc = doc[pos-30:pos+30]
                linkend = doc.find(' title=') - 1
                linkpos = doc.find('http')
                bookfidl = doc[linkpos:linkend]
                print bookfidl
                s.downloads[extension + ' (via bookfi)'] = bookfidl

                s.formats = extension
                yield s
                counter = counter + 1
