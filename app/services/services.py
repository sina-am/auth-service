from app.services.authentication import AuthenticationService
from app.services.verification import SMSVerificationService
from app.database import Database
from app.cache import Cache


__srv: AuthenticationService

def init_srv(srv: AuthenticationService):
    global __srv
    __srv = srv


def get_srv() -> AuthenticationService:
    # TODO: raise a proper error
    if not __srv:
        raise TypeError("service is not initiated yet")
    return __srv