import asyncio
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi

from app.services import get_srv
from app.models.response import Message, StandardResponse
from app.apis.router import router
from app.services.rpc import call_service

from app.core import errors


app = FastAPI(prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Authentication Microservice",
        description="",
        version="0.0.1",
        routes=app.routes,
    )
    openapi_schema["components"]["schemas"]["HTTPValidationError"] = {
        "title": "HTTPValidationError",
        "required": [
            "message"
        ],
        "type": "object",
                "properties": {
                    "message": {
                        "$ref": "#/components/schemas/Message"
                    }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
def startup():
    service = get_srv()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(service.broker.consume(
        loop, 'auth_srv', call_service))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        content=StandardResponse(message=Message(
            en=exc.errors()[0]['msg'], fa=None)).dict(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.exception_handler(HTTPException)
async def exception_handler(request, exc: HTTPException):
    return JSONResponse(
        content=StandardResponse(message=Message(
            en=exc.detail, fa=None)).dict(),
        status_code=exc.status_code
    )


@app.exception_handler(errors.MyException)
async def custom_error_handler(request, exc: errors.MyException):
    return JSONResponse(
        content=StandardResponse(message=Message(en=str(exc), fa=None)).dict(),
        status_code=status.HTTP_400_BAD_REQUEST
    )
