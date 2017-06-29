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

        lg=libgenapi.Libgenapi(["http://libgen.io","http://gen.lib.rus.ec","http://93.174.95.27/","http://libgen.in","http://libgen.org"])
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
                cover = 'http://gen.lib.rus.ec' + cover
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
                libgenformat = 'libgen: .' + extension
                s.downloads[libgenformat] = libgendl

                #get download location from libgen.pw
                lgpw = r['mirrors'][0].replace('view', 'download')
                with closing(br.open(lgpw, timeout=10)) as f:
                    doc = f.read()
                pos = doc.find('location') + 16
                end = doc.find('status') - 27
                location = doc[pos:end]

                #prep filename
                filename = r['author'] + ' - ' + r['title']
                filename = filename.replace(' ', '_')
                filename = filename.encode('utf8')
                filename = urllib2.quote(filename)

                #prep download via b-ok (/bookzz/boosc/bookza)
                bokdl = 'http://dlx.b-ok.org/genesis/' + location + '/_as/' + filename + '.pdf'
                bokformat = 'b-ok: .' + extension
                s.downloads[bokformat] = bokdl

                #prep download via bookfi
                bookfidl = 'http://dl.lux.bookfi.net/genesis/' + location + '/_as/' + filename + '.pdf'
                bookfiformat = 'bookfi: .' + extension
#                s.downloads[bookfiformat] = bookfidl

                s.formats = libgenformat + ', ' + bokformat + ', ' + bookfiformat + ','
                yield s
                counter = counter + 1
