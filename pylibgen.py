"""
MIT License

Copyright (c) 2018 Mudew
Copyright (c) 2017 Joshua Li

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import os
import re
import webbrowser
from urllib import quote_plus
from . import constants, requests


class Library(object):
    """Library Genesis interface wrapper."""

    def __init__(self, mirror=constants.DEFAULT_MIRROR):
        assert(mirror in constants.MIRRORS)
        self.mirror = mirror

    def __repr__(self):
        return '<Library using mirror {}>'.format(self.mirror)

    def __str__(self):
        return self.__repr__

    def search(self, query, type='title'):
        """Searches Library Genesis.

        Note:
            For search type isbn, either ISBN 10 or 13 is accepted.

        Args:
            query (str): Search query.
            type (str): Query type. Can be title, author, isbn.

        Returns:
            List of LibraryGenesis book IDs that matched the query.
        """
        assert(type in {'title', 'author', 'isbn'})
        r = self.__req('search', {
            'req': quote_plus(query),
            'column': type,
        })
        return re.findall("<tr.*?><td>(\d+)", r.text)

    def lookup(self, ids, fields=constants.DEFAULT_FIELDS):
        """Looks up metadata on Library Genesis books.

        Note:
            To get book IDs, use search(). The default fields
            suffice for most use cases, but there are a LOT more
            like openlibraryid, publisher, etc. To get all fields,
            use fields=['*'].

        Args:
            ids (list): Library Genesis book IDs.
            fields (list): Library Genesis book properties.

        Returns:
            List of dicts each containing values for the specified
            fields for a Library Genesis book ID.
            A single dict if only one str or int id is passed in.
        """
        # Allow for lookup of a single numeric string by auto casting
        # to a list for convenience.
        if isinstance(ids, (str, int)):
            ids = [str(ids)]
        res = self.__req('lookup', {
            'ids': ','.join(ids),
            'fields': ','.join(fields),
        }).json()
        if not res:
            # https://github.com/JoshuaRLi/pylibgen/pull/3
            raise requests.HTTPError(400)
        return res if len(res) > 1 else res[0]

    def get_download_url(self, md5, enable_ads=False):
        """Gets a direct download URL to a Library Genesis book.

        Note:
            This is actually specific only to the libgen.io mirror!
            Will need to be rewritten if things change.
            Use lookup() to obtain the MD5s for Library Genesis books.
            To support Library Genesis, pass True to enable_ads.
            See the package README for more detail.

        Args:
            md5 (str): Library Genesis unique book identifier checksum.
            enable_ads (bool): Toggle ad bypass via direct download key
                scraping.

        Returns:
            A direct download URL.
        """
        url = self.__req('download', {'md5': md5}, urlonly=True)
        if enable_ads:
            return url
        r = self.__req('download', {'md5': md5})
        key = re.findall("&key=(.*?)'", r.text)[0]
        return '{}&key={}'.format(url, key)

    def download(self, md5, dest='.', use_browser=False):
        """Downloads a Library Genesis book.

        Note:
            Libgen seems to delay programmatically sent dl requests, even
            if the UA string is spoofed and the URL contains a good key,
            so I recommend just using get_download_url. Alternatively, you
            can set use_browser=True, which will just open up the download
            URL in a new browser tab.

            Note that if you spam download requests, libgen will temporarily
            503. Again, I recommend using get_download_url and downloading
            from the browser.

        Args:
            md5 (str): Library Genesis unique book identifier checksum.
            dest (str): Path to download directory.
            use_browser (bool): Use browser to download instead.
        """
        auth_url = self.get_download_url(md5, enable_ads=False)
        if use_browser:
            webbrowser.open_new_tab(auth_url)
            return
        r = requests.get(auth_url)
        r.raise_for_status()
        with open(os.path.join(dest, md5), 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

    def __req(self, endpoint, getargs, urlonly=False):
        url = constants.ENDPOINTS[endpoint].format(
            mirror=self.mirror, **getargs
        )
        if urlonly:
            return url
        r = requests.get(url)

        # ugly patch for the decoder to properly detect the response as json
        if r.content.startswith('id['):
            r.content = r.content[2:]

        r.raise_for_status()
        return r
