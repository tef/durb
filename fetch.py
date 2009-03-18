# library around pycurl and it's barebones c-like interface

import StringIO
import re

from urlparse import urlparse,urlunparse
from urllib import urlencode

import pycurl

__all__ = [ "fetch", "Session" ]

def fetch(resource, **options):
    s = Session()
    return s.fetch(resource, **options)

class Session(object):
    """A session contains defaults for fetching resources, 
    as well as keeping the http referer"""

    def __init__(self, **options):
        self.curl = pycurl.Curl()
        self.options = options

    def fetch(self, resource, **options):
        opts = self.options.copy()
        opts.update(options)
        opts = self.curl_setup(opts)

        response = StringIO.StringIO()
        headers = StringIO.StringIO()

        self.curl.setopt(pycurl.WRITEFUNCTION, response.write)
        self.curl.setopt(pycurl.HEADERFUNCTION, headers.write)

        opts = self.fetch_setup(resource, opts)

        self.curl.perform()

        response_code = self.curl.getinfo(pycurl.RESPONSE_CODE)
        content_type = self.curl.getinfo(pycurl.CONTENT_TYPE)

        charset = opts.pop("charset",None)

        if not charset and content_type:
                charset = extract_charset(content_type) 

        location = self.curl.getinfo(pycurl.EFFECTIVE_URL)
        
        return Response({
            'response_code' : response_code,
            'raw_data': response.getvalue(),
            'data_charset': charset,
            'headers' : decode_headers(headers.getvalue()),
            'url': location,
            })

    def fetch_setup(self, resource, options):
        curl = self.curl
        
        get = options.pop("get", None)
        if get:
            url = resource + "?" + url_encode(get)
        else:
            url = resource

        curl.setopt(pycurl.URL, url)

        post = options.pop("post", None)
        if post:
            post = url_encode(post)

            curl.setopt(pycurl.POSTFIELDS, post)
            curl.setopt(pycurl.POST,1)
        else:
            curl.setopt(pycurl.HTTPGET,1)

        return options

    def curl_setup(self, options):
        curl = self.curl
        proxy = options.pop("proxy",None)
        if proxy:
            curl.setopt(pycurl.PROXY,proxy)

        verify_ssl = options.pop("verify_ssl",0)
        verify_ssl = int(bool(verify_ssl))
        curl.setopt(pycurl.SSL_VERIFYPEER,verify_ssl)

        user_agent = options.pop("user_agent",False)
        if user_agent is None:
            curl.setopt(pycurl.USERAGENT,"")
        elif user_agent:
            curl.setopt(pycurl.USERAGENT,user_agent)

        gzip = options.pop("gzip",True)
        if gzip:
            curl.setopt(pycurl.ENCODING,"gzip, deflate")
        else:
            curl.setopt(pycurl.ENCODING,"")

        curl.setopt(pycurl.FOLLOWLOCATION, 1)

        return options

class Response(dict):
    def text(self, charset=None):
        if charset is None:
            charset = self['data_charset']
        return unicode(self['raw_data'].decode(charset,"xmlcharrefreplace"))

def decode_headers(headers_text):
    headers = []
    for line in headers_text.splitlines():
        if line.find(":") > 0:
            name, value = line.split(":",1)
            headers.append((name,value))
        else:
            headers.append(line)
    return headers
    
rx = re.compile("charset=([\w-]+)", re.U|re.I)

def extract_charset(header):
    o = rx.search(header)
    if o:
        return o.groups()[0]
    else:
        return None
    

def url_encode(data):
    if isinstance(data, dict):
        return urlencode(data)
    elif isinstance(data, unicode):
        return data.encode("utf-8")
    else:
        return str(data)
