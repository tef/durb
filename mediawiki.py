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
         out =  self.http.fetch(self.url, post=params)
         #print out.text()
         return  out.xml()

    def login(self, username, password):
        r = self._fetch(action="login", lgname=username, lgpassword=password)
        o = r.xpath('/api/login/@result[. = "Success"]')
        return o and o[0] == "Success"

    def logout(self):
        self._fetch(action="logout")

    def get_edit_token(self, page_title):
        r = self._fetch(action="query", prop="info|revisions", intoken="edit", titles=page_title)
        token = r.xpath('/api/query/pages/page[@title = "%s"]/@edittoken'%page_title)
        token = token[0] if len(token) > 0 else None
        last_rev= r.xpath('/api/query/pages/page[@title = "%s"]/@touched'%page_title)
        last_rev = last_rev[0] if len(last_rev) > 0 else None

        return (token, last_rev)

    def edit(self,token, title, text):
        edit_token, timestamp = token
        args = dict(
            action="edit",
            title=title, 
            text=text,
            token=edit_token
        )
        if timestamp:
            args["starttimestamp"]=timestamp
        r = self._fetch(**args)

        return etree.tostring(r)


