import urllib.request, urllib.parse, html, json
from .base import Backend
from ..error import EJError
from .openerwr import OpenerWrapper

class YaContest(Backend):
    @staticmethod
    def detect(url):
        if url.endswith('/'): url = url[:-1]
        if url.endswith('/enter'): url = url[:-6]
        return url.startswith('https://contest.yandex.ru/contest/') and url[34:].isnumeric()
    @staticmethod
    def _get_bem(data, sp):
        return json.loads(html.unescape(data.split(sp, 1)[1].split('"', 1)[0]))
    @classmethod
    def _get_sk(self, data):
        try: return data.split('<input type="hidden" name="sk" value="', 1)[1].split('"', 1)[0]
        except IndexError: return self._get_bem(data, '<div class="aside i-bem" data-bem="')['aside']['sk']
    def __init__(self, url, login, passwd):
        if url.endswith('/'): url = url[:-1]
        if url.endswith('/enter'): url = url[:-6]
        if not self.detect(url):
            raise EJError("Not a contest.yandex.ru URL")
        self.opener = OpenerWrapper(urllib.request.build_opener(urllib.request.HTTPCookieProcessor))
        data = self.opener.open('https://passport.yandex.ru/auth?'+urllib.parse.urlencode({'origin': 'consent', 'retpath': url}), urllib.parse.urlencode({'login': login, 'passwd': passwd}).encode('ascii'))
        if data.geturl() != url+'/enter/':
            raise EJError('Login failed.')
        self.url = url
    def do_action(self, action, *args):
        try: url = self.url + {'stop_virtual': '/finish/?return=false', 'restart_virtual': '/finish/?return=true'}[action]
        except KeyError: pass
        else:
            #WIP, doesn't work yet
            try: return self.opener.open(url, urllib.parse.urlencode({'sk': self._get_sk(self.opener.open(self.url).read().decode('utf-8', 'replace'))}).encode('ascii')).read() == b'OK'
            except urllib.request.URLError: return False
        action = {'register': 'register', 'start_virtual': 'startVirtual'}[action]
        try: data = self.opener.open(self.url, urllib.parse.urlencode({'sk': self._get_sk(self.opener.open(self.url).read().decode('utf-8', 'replace')), 'action': action, 'retpath': self.url}).encode('ascii'))
        except urllib.request.URLError: return False
        url = data.geturl()
        return url.split('?', 1)[0] == self.url and '?error=' not in url
