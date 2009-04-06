import mediawiki
import lxml.etree as etree

def loadpw(filename):
    fh = open(filename)
    lines = "".join(x.strip() for x in fh.readlines())
    return lines.split(":",1)

un,pw = loadpw("passwd")
def mw(text):
    a = mediawiki.Session("http://www.includipedia.com/mediawiki-1.14.0/api.php")
    print a.login(un,pw)
    token = a.get_edit_token("Includipedia:TestPageOnly")
    print a.edit(token,"Includipedia:TestPageOnly",text)
    print a.logout()

def wp(text):
    a = mediawiki.Session("http://en.wikipedia.org/w/api.php")
    token = a.get_edit_token("Wikipedia:Sandbox")
    print  a.edit(token,"Wikipedia:Sandbox","thisisatest")

import sys
if __name__ == '__main__':
    mw("".join(str(x) for x in sys.argv[1:]))
