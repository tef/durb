"""mediawiki api wrapper for python """
import lxml.etree as etree

import fetch


class Session(object):
    """A session object handles the api connection and provides
       methods for interacting with the server"""

    def __init__(self, base_url):
        self.http = fetch.Session()
        self.url = base_url

    def _fetch(self, **params):
         params['format'] = 'xml'
         return self.http.parse(self.url, post=params)['xml']

    def login(self, username, password):
        r = self._fetch(action="login", lgname=username, lgpassword=password)
        return bool(r.xpath('/api/login/@result[. = "Success"]')[0])

    def logout(self):
        self._fetch(action="logout")

    def get_edit_token(self, page_title):
        r = self._fetch(action="query", prop="info|revisions", intoken="edit", titles=page_title)
        token = r.xpath('/api/query/pages/page[@title = "%s"]/@edittoken'%page_title)[0]
        last_rev= r.xpath('/api/query/pages/page[@title = "%s"]/@lastrevid'%page_title)[0]

        return (token, last_rev)

