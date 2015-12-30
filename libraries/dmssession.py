__author__ = 'michael'
import web
from web.session import Session

class DMSSessionExpired(web.HTTPError):
    def __init__(self, headers,message):
        web.HTTPError.__init__(self, '200 OK', headers, data=message)

class DMSSession(Session):
    def __init__(self, app, store, initializer=None):
        Session.__init__(self,app,store,initializer)

    def expired(self):
        self._killed = True
        self._save()
        message = self._config.expired_message
        headers = {'Content-Type': 'text/html','Refresh':'1;url="/dms/admin/login"'}
        raise DMSSessionExpired(headers, message)
