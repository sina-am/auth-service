from app.core.errors import MyException


class DatabaseConnectionError(MyException):
    ...


class DatabaseInitError(MyException):
    ...


class InvalidDatabaseSchema(MyException):
    ...


class RecordDoesNotExist(MyException):
    ...


class UserDoesNotExist(MyException):
    ...


class UserAlreadyExist(MyException):
    ...


class RoleAlreadyExist(MyException):
    ...


class RoleDoesNotExist(MyException):
    ...


class CityDoesNotExist(MyException):
    ...
