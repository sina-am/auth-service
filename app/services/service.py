from app.database import Database
from app.cache import Cache
from app.services.broker import Broker
from app.services.verification import SMSNotification, SMSVerificationService
from app.services.authentication import AuthService


def authentication_factory(db: Database, cache: Cache, broker: Broker, notification: SMSNotification) -> AuthService:
    return AuthService(
        broker=broker,
        db=db,
        cache=cache,
        verification=SMSVerificationService(
            notification=notification, cache=cache, db=db)
    )
