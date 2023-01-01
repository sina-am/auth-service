from app.models.response import Message, StandardResponse


def standard_response(message: str) -> StandardResponse:
    return StandardResponse(message=Message(en=message))