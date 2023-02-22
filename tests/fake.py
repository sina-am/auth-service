from app.models.user import RealUser
from app.services.token import get_access_token


def get_admin_token(admin: RealUser) -> str:
    return get_access_token(admin, '*', 'admin')
