from pydantic import BaseModel, validator
from app.utils.translation import fa


class Message(BaseModel):
    en: str
    fa: str = None
     
    @validator("fa", pre=True, always=True)
    def translate_message(cls, v, values, **kwargs):
        if not v:
            en_message = values.get("en")
            if en_message:
                return fa.gettext(en_message)
            return ""
        return v


class StandardResponse(BaseModel):
    """
    Standard response for successful messages and also errors.
    """
    message: Message