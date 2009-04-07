#!/usr/bin/env python
"""mediawiki api wrapper for python """
import sys
import getpass
import os.path
from optparse import OptionParser

import lxml.etree as etree

import fetch

parser = OptionParser()
parser.add_option("-T", "--title", dest="title", help="title of page")
parser.add_option("-t", "--text", dest="text", help="text of page")
parser.add_option("-f", "--file", dest="file", help="file with text")
parser.add_option("-A", "--auth", dest="auth", metavar="FILE",help="file with auth")

default_auth = os.path.expanduser("~/.mediawiki")
mw_url = "http://www.includipedia.com/mediawiki-1.14.0/api.php"

def main(argv):
    command = argv.pop(0).lower()
    (options, args) = parser.parse_args(argv)
    c = Command(command,options, args)
    try:
        c.run()
    except BaseException, e:
        sys.stderr.write("error: %s\n" % e)
    

class Command(object):
    def __init__(self, command, options, args):
        self.options = options
        self.args = args
        self.run = getattr(self,command)
        s = Session(mw_url)

    def login(self):
        print "username:"
        user = raw_input()
        pw = getpass.getpass("password:")


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



if __name__ == "__main__":
    main(sys.argv[1:])



