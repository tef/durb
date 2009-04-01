"""mediawiki api wrapper for python """
import fetch


class Session(object):
    """A session object handles the api connection and provides
       methods for interacting with the server"""

    def __init__(self, base_url):
        self.http = fetch.Session()
        self.url = base_url

    def _fetch(self, **params):
         params['format'] = 'xml'
         output = self.http.fetch(self.url, post=params)
         return output.text()

    def login(self, username, password):
        return self._fetch(action="login", lgname=username, lgpassword=password)

    def logout(self):
        return self._fetch(action="logout")


