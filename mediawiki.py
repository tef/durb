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
parser.add_option("-U", "--url", dest="url",help="mediawiki url")

default_auth = os.path.expanduser("~/.mediawiki")
mw_url = "http://www.includipedia.com/mediawiki-1.14.0/api.php"

def main(argv):
    if not argv[0].startswith("-"):
        action = argv.pop(0).lower()
    else:
        action = None

    (options, args) = parser.parse_args(argv)
    url = options.url or mw_url
    auth_file = options.auth or default_auth
    un, pw = read_creds(auth_file, url)

    try:
        s = Session(url)
        if action == "login":
            un,pw = ask_creds()
            if s.login(un,pw):
                write_creds(auth_file, un, pw, url)
        else:
            if un and pw:
                if not s.login(un,pw):
                    raise Exception, "failed to login"
            if action == "edit":
                text = options.text
                if not text:
                    file = options.file 
                    if file and file != "-":
                        fh = open(file, "r")
                        text = "".join(fh.readlines())
                        fh.close()
                    else:
                        text = "".join(sys.stdin.readlines())
                    
                title = options.title or "Includipedia:TestPageOnly"
                token = s.get_edit_token(title)
                s.edit(token, title, text)

        s.logout()
    except BaseException, e:
        sys.stderr.write("error: %s\n" % e)


def read_creds(filename, url):
    """Given a url, read the credentials for it"""
    try:
        fh = open(filename,"r")
    except:
        return None, None
    
    un, pw = None,None
    for line in fh.readlines():
        un_, pw_, url_ = line.strip().split(":",2)
        if url == url_:
            un, pw = un_, pw_
            break
    fh.close()
    return un,pw

def write_creds(filename, un,pw, url):
    """write the new credentials into the savefile, preserving existing creds that do not overlap"""
    try:
        fh = open(filename,"r")
        creds = fh.readlines()
        fh.close()
    except:
        creds = []

    fh = open(filename,"w")
    fh.write("%s:%s:%s\n"%(un,pw,url))
    for line in creds:
        un_, pw_, url_ = line.strip().split(":",2)
        if url != url_:
            fh.write("%s:%s:%s\n"%(un_,pw_,url_))
    fh.close()


def ask_creds():
        """prompt the user for credentials"""
        print "username:",
        user = raw_input()
        pw = getpass.getpass("password:")
        return user,pw

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



