from json import JSONEncoder

from typing import Any
from datetime import date, datetime

from bson import ObjectId
from app.core.config import settings


class JsonSerializer(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime) or isinstance(o, date):
            return o.strftime(format=settings.datetime_format)
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)
