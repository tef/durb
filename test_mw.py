import mediawiki
import lxml.etree as etree

def loadpw(filename):
    fh = open(filename)
    lines = "".join(x.strip() for x in fh.readlines())
    return lines.split(":",1)

un,pw = loadpw("passwd")
print un,pw
def mw():
    a = mediawiki.Session("http://www.includipedia.com/mediawiki/api.php")
    print a.login(un,pw)
    token = a.get_edit_token("Includipedia:TestPageOnly")
    print a.edit(token,"Includipedia:TestPageOnly","thisisatest")
    print a.logout()

def wp():
    a = mediawiki.Session("http://en.wikipedia.org/w/api.php")
    token = a.get_edit_token("Wikipedia:Sandbox")
    print  a.edit(token,"Wikipedia:Sandbox","thisisatest")


mw()
