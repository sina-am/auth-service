from app.services.authentication import AuthService


__srv: AuthService

def init_srv(srv: AuthService):
    global __srv
    __srv = srv


def get_srv() -> AuthService:
    # TODO: raise a proper error
    if not __srv:
        raise TypeError("service is not initiated yet")
    return __srv