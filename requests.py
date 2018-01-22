import urllib2
import codecs
import json
import httplib

# A monkey patch for the requests library.

bytes = str
str = unicode

CONTENT_CHUNK_SIZE = 10 * 1024

# Null bytes; no need to recreate these on each call to guess_json_utf
_null = '\x00'.encode('ascii')  # encoding to ASCII for Python 3
_null2 = _null * 2
_null3 = _null * 3

def guess_json_utf(data):
    """
    :rtype: str
    """
    # JSON always starts with two ASCII characters, so detection is as
    # easy as counting the nulls and from their location and count
    # determine the encoding. Also detect a BOM, if present.
    sample = data[:4]
    if sample in (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE):
        return 'utf-32'     # BOM included
    if sample[:3] == codecs.BOM_UTF8:
        return 'utf-8-sig'  # BOM included, MS style (discouraged)
    if sample[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        return 'utf-16'     # BOM included
    nullcount = sample.count(_null)
    if nullcount == 0:
        return 'utf-8'
    if nullcount == 2:
        if sample[::2] == _null2:   # 1st and 3rd are null
            return 'utf-16-be'
        if sample[1::2] == _null2:  # 2nd and 4th are null
            return 'utf-16-le'
        # Did not detect 2 valid UTF-16 ascii-range characters
    if nullcount == 3:
        if sample[:3] == _null3:
            return 'utf-32-be'
        if sample[1:] == _null3:
            return 'utf-32-le'
        # Did not detect a valid UTF-32 ascii-range character
    return None

def patch(obj, method):
    name = method.__name__
    setattr(obj, name, types.MethodType(method, obj))

def iter_slices(string, slice_length):
    """Iterate over slices of a string."""
    pos = 0
    if slice_length is None or slice_length <= 0:
        slice_length = len(string)
    while pos < len(string):
        yield string[pos:pos + slice_length]
        pos += slice_length

class HTTPError(urllib2.HTTPError):
    def __init__(self, code, url="", msg=None):
        urllib2.HTTPError.__init__(self, url, code=code,
                msg=httplib.responses.get(code, "") if msg is None else msg,
                hdrs=None, fp=None)

class RequestWrapper:
    def __init__(self, resp):
        self.resp = resp
        self.encoding = self.resp.headers.getparam('charset') 
        self.status_code = self.resp.getcode()
        self._content = False
        self._content_consumed = False

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size=1):

        def generate():
            # Standard file-like object.
            while True:
                chunk = self.resp.read(chunk_size)
                if not chunk:
                    break
                yield chunk

            self._content_consumed = True

        if self._content_consumed and isinstance(self._content, bool):
            raise StreamConsumedError()
        elif chunk_size is not None and not isinstance(chunk_size, int):
            raise TypeError("chunk_size must be an int, it is instead a %s." % type(chunk_size))
        
        # simulate reading small chunks of the content
        reused_chunks = iter_slices(self._content, chunk_size)

        stream_chunks = generate()

        chunks = reused_chunks if self._content_consumed else stream_chunks

        return chunks
        


    @property
    def content(self):
        """Content of the response, in bytes."""
        if self._content is False:
            self._content = bytes().join(self.iter_content(CONTENT_CHUNK_SIZE)) or bytes()

        self._content_consumed = True
        return self._content

    @property
    def text(self):
        if not self.content:
            return str('')

        try:
            content = str(self.content, self.encoding, errors='replace')
        except (LookupError, TypeError):
            # A LookupError is raised if the encoding was not found which could
            # indicate a misspelling or similar mistake.
            #
            # A TypeError can be raised if encoding is None
            #
            # So we try blindly encoding.
            content = str(self.content, errors='replace')

        return content

    def json(self, **kwargs):
        r"""Returns the json-encoded content of a response, if any.
        :param \*\*kwargs: Optional arguments that ``json.loads`` takes.
        :raises ValueError: If the response body does not contain valid json.
        """

        if not self.encoding and self.content and len(self.content) > 3:
            # No encoding set. JSON RFC 4627 section 3 states we should expect
            # UTF-8, -16 or -32. Detect which one to use; If the detection or
            # decoding fails, fall back to `self.text` (using chardet to make
            # a best guess).
            encoding = guess_json_utf(self.content)
            if encoding is not None:
                try:
                    return json.loads(
                        self.content.decode(encoding), **kwargs
                    )
                except UnicodeDecodeError:
                    # Wrong UTF codec detected; usually because it's not UTF-8
                    # but some other 8-bit codec.  This is an RFC violation,
                    # and the server didn't bother to tell us what codec *was*
                    # used.
                    pass
        return json.loads(self.text, **kwargs)
    

def get(url):
  r = urllib2.urlopen(url)
  return RequestWrapper(r)

