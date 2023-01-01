""" Simple CLI just to quickly create a default user and a role. """

import sys
from getpass import getpass
from app.models.user import RealUser
from app.models.role import UserRole, Role


def create_admin():
    from app.database import storage
    national_code = input("National Code: ")
    phone_number = input("Phone number:" )
    first_name = input("First name: ")
    last_name = input("Last name: ")
    password = getpass("Password: ")

    if not storage.roles.get_by_platform('*'):
        storage.roles.create(Role(platform='*', names=['admin']))

    admin = RealUser.new_user(
        national_code, 
        phone_number, 
        first_name, 
        last_name, 
        password, 
        [UserRole(platform='*', names=['admin'])]
    )

    storage.users.create(admin)


def main():
    if len(sys.argv) != 2 or sys.argv[1] != 'create-admin':
        print(f"use: python {sys.argv[0]} create-admin")
        return
    create_admin()


if __name__ == '__main__':
    main()