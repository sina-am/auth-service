import asyncio
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.models.response import Message, StandardResponse
from app.apis.router import router
from app.services import RabbitMQ
from app.services import init_srv, AuthenticationService, SMSVerificationService, FakeSMSNotification
from app.database import MongoDatabase, init_db
from app.cache import RedisCache, init_cache
from app.core.config import settings
from app.core import errors
from fastapi.openapi.utils import get_openapi


"""
Main asgi application for running with uvicorn
"""


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


@app.on_event('startup')
async def startup():
    db = MongoDatabase(settings.mongodb.uri, settings.mongodb.database)
    init_db(db)

    cache = RedisCache(
        settings.redis.address.host, # type: ignore
        settings.redis.address.port, # type: ignore 
        db=0, 
        password=settings.redis.password # type: ignore
    )
    init_cache(cache)

    service = AuthenticationService(
        verification=SMSVerificationService(
            notification=FakeSMSNotification()
        )
    )
    init_srv(service)

    rabbitmq =  RabbitMQ(
        settings.rabbitmq.address, 
        settings.rabbitmq.port, 
        settings.rabbitmq.username, 
        settings.rabbitmq.password
    )

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(rabbitmq.consume(loop))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        content=StandardResponse(message=Message(en=exc.errors()[0]['msg'], fa=None)).dict(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
  
@app.exception_handler(HTTPException)
async def exception_handler(request, exc: HTTPException):
    return JSONResponse(
        content=StandardResponse(message=Message(en=exc.detail, fa=None)).dict(),
        status_code=exc.status_code
    )

@app.exception_handler(errors.MyException)
async def custom_error_handler(request, exc: errors.MyException):
    return JSONResponse(
        content=StandardResponse(message=Message(en=str(exc), fa=None)).dict(),
        status_code=status.HTTP_400_BAD_REQUEST
    )