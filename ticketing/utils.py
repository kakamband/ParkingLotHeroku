import jwt,os
from django.conf import settings
import traceback
from rest_framework.request import Request

def is_login(function):
    def wrapper(*args, **kw):
        try:
            token = args[-1].COOKIES['jwt']
            if token:
                payload = jwt.decode(token, settings.SECRET_KEY)
                userid = payload['id']
                return function(id=userid, *args, **kw)
        except:
            return function(id=None, *args, **kw)
    return wrapper