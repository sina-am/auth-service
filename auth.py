#!/usr/bin/python3

import uvicorn
import typer
import rich


from app.services import (
    RabbitMQ, authentication_factory,
    init_srv, MelipayamakSMSNotification, FakeSMSNotification)
from app.database import MongoDatabase
from app.cache import RedisCache
from app.core.config import settings
from app.types.fields import PhoneNumberField, NationalCodeField


service = authentication_factory(
    db=MongoDatabase(
        settings.mongodb.uri,
        settings.mongodb.database
    ),
    broker=RabbitMQ(
        settings.rabbitmq.address,
        settings.rabbitmq.port,
        settings.rabbitmq.username,
        settings.rabbitmq.password
    ),
    cache=RedisCache(
        settings.redis.address.host,  # type: ignore
        settings.redis.address.port,  # type: ignore
        db=0,
        password=settings.redis.password  # type: ignore
    ),
    notification=FakeSMSNotification()
)
init_srv(service)

cli = typer.Typer()


@cli.command()
def run(host: str = "localhost", port: int = 8080, debug: bool = False):
    """ Run API server with uvicorn """

    if debug:
        app = "app.web:app"
    else:
        from app.web import app
        app.debug = debug

    uvicorn.run(app, reload=debug, host=host, port=port)  # type: ignore


@cli.command()
def get_users():
    console = rich.get_console()
    console.print(
        list(map(lambda x: dict(x), service.database.users.get_all())))


@cli.command()
def create_admin():
    """ Create an admin user """
    console = rich.get_console()
    console.rule("Registration")
    admin = service.create_admin(
        national_code=NationalCodeField(
            console.input("Enter national code: ")),
        phone_number=PhoneNumberField(console.input("Enter phone number: ")),
        first_name=console.input("Enter first name: "),
        last_name=console.input("Enter last_name name: "),
        password=console.input("Enter password: ", password=True)
    )

    console.print(
        f"Welcome! {admin.first_name}, {admin.last_name}.")


if __name__ == '__main__':
    cli()
