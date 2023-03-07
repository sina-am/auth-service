from unittest import TestCase
from app.database import MongoDatabase, MemoryDatabase, errors
from app.models.province import Province, City
from app.models.role import Role, UserRole
from app.models.user import RealUser, LegalUser
from app.models.profile import ContactInformation
from bson import ObjectId
from app.types.fields import ObjectIdField, NationalCodeField, PhoneNumberField, CompanyCodeField


class TestDatabaseProvinceCollection(TestCase):
    def setUp(self):
        self.database = MongoDatabase("mongodb://localhost", "test_database")

    def tearDown(self) -> None:
        self.database.drop()

    def test_create(self):
        province = Province(
            _id=ObjectIdField(ObjectId()),
            name='p1',
            cities=[
                City(_id=ObjectIdField(ObjectId()), name='c11'),
                City(_id=ObjectIdField(ObjectId()), name='c12')
            ]
        )

        self.database.provinces.create(province)
        assert province.id

    def test_get_all(self):
        provinces = [
            Province(
                _id=ObjectIdField(ObjectId()),
                name='p1',
                cities=[
                    City(_id=ObjectIdField(ObjectId()), name='c11'),
                    City(_id=ObjectIdField(ObjectId()), name='c12')
                ]
            ),
            Province(
                _id=ObjectIdField(ObjectId()),
                name='p2',
                cities=[
                    City(_id=ObjectIdField(ObjectId()), name='c21'),
                    City(_id=ObjectIdField(ObjectId()), name='c22')
                ]
            ),
        ]
        for province in provinces:
            self.database.provinces.create(province)

        db_provinces = self.database.provinces.get_all()
        assert db_provinces == provinces

    def test_get_by_city_id(self):
        city = City(_id=ObjectIdField(ObjectId()), name='c13')

        province = Province(
            _id=ObjectIdField(ObjectId()),
            name='p1',
            cities=[
                City(_id=ObjectIdField(ObjectId()), name='c11'),
                City(_id=ObjectIdField(ObjectId()), name='c12'),
                city
            ]
        )
        self.database.provinces.create(province)

        db_province = self.database.provinces.get_by_city_id(str(city.id))
        assert city == db_province.cities[0]


class TestDatabaseRoleCollection(TestCase):
    def setUp(self):
        self.database = MongoDatabase("mongodb://localhost", "test_database")

    def tearDown(self) -> None:
        self.database.drop()

    def test_create(self):
        role = Role(
            _id=ObjectIdField(ObjectId()),
            platform="*",
            names=['admin', 'staff']
        )
        self.database.roles.create(role)
        assert role.id

    def test_create_on_already_exists_platform(self):
        role = Role(
            _id=ObjectIdField(ObjectId()),
            platform="*",
            names=['admin', 'staff']
        )
        self.database.roles.create(role)

        try:
            self.database.roles.create(role)
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.RoleAlreadyExist)

    def test_get_by_platform(self):
        role = Role(
            _id=ObjectIdField(ObjectId()),
            platform="*",
            names=['admin', 'staff']
        )
        self.database.roles.create(role)

        db_role = self.database.roles.get_by_platform('*')
        assert db_role == role

    def test_get_none_existent_role(self):
        role = Role(
            _id=ObjectIdField(ObjectId()),
            platform="test2",
            names=['admin', 'staff']
        )
        self.database.roles.create(role)

        try:
            self.database.roles.get_by_platform('test')
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.RoleDoesNotExist)

    def test_get_all_on_none_list(self):
        db_roles = self.database.roles.get_all()
        assert db_roles == []
        assert db_roles is not None

    def test_get_all(self):
        roles = [
            Role(
                _id=ObjectIdField(ObjectId()),
                platform="platform1",
                names=['admin', 'staff']
            ),
            Role(
                _id=ObjectIdField(ObjectId()),
                platform="platform2",
                names=['admin', 'staff']
            ),
            Role(
                _id=ObjectIdField(ObjectId()),
                platform="platform3",
                names=['admin', 'staff']
            )
        ]
        for role in roles:
            self.database.roles.create(role)

        db_roles = self.database.roles.get_all()
        assert roles == db_roles


class TestDatabaseUserCollection(TestCase):
    def setUp(self):
        self.database = MongoDatabase("mongodb://localhost", "test_database")
        # Raise error if database connection failed
        self.database.check_connection()

        self.province = Province(
            _id=ObjectIdField(ObjectId()),
            name='p1',
            cities=[
                City(_id=ObjectIdField(ObjectId()), name='c11'),
                City(_id=ObjectIdField(ObjectId()), name='c12')
            ]
        )
        self.database.provinces.create(self.province)

        role = Role(
            _id=ObjectIdField(ObjectId()),
            platform="*",
            names=['admin', 'staff']
        )
        self.database.roles.create(role)

    def tearDown(self) -> None:
        self.database.drop()

    def test_create_real_user(self):
        user = RealUser.new_user(
            national_code=NationalCodeField('1'*10),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1'*10),
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        db_user = self.database.users.create(user)

        assert db_user == user

    def test_create_real_user_with_none_existent_platform(self):
        user = RealUser.new_user(
            national_code=NationalCodeField('1'*10),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1'*10),
            plain_password='plain_password',
            roles=[
                UserRole(platform='invalid_platform', names=['admin'])
            ],
        )
        try:
            self.database.users.create(user)
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.RoleDoesNotExist)

    def test_create_real_user_with_invalid_province(self):
        user = RealUser.new_user(
            national_code=NationalCodeField('1'*10),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1'*10),
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        user.contact_information = ContactInformation(
            city_id=ObjectIdField(ObjectId()))  # type: ignore

        try:
            self.database.users.create(user)
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.CityDoesNotExist)

    def test_create_already_exist_real_user(self):
        user = RealUser.new_user(
            national_code=NationalCodeField('1'*10),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1'*10),
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        db_user = self.database.users.create(user)

        with self.assertRaises(errors.UserAlreadyExist):
            self.database.users.create(user)

    def test_get_real_user_by_national_code(self):
        user = RealUser.new_user(
            national_code=NationalCodeField('1'*10),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1'*10),
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.database.users.create(user)

        db_user = self.database.users.get_by_national_code(
            NationalCodeField(user.national_code))

        assert db_user == user

    def test_get_none_existent_real_user(self):
        user = RealUser.new_user(
            national_code=NationalCodeField('1'*10),
            first_name='first_name',
            last_name='last_name',
            phone_number=PhoneNumberField('1'*10),
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.database.users.create(user)

        try:
            self.database.users.get_by_national_code(
                NationalCodeField('2'*10))
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.UserDoesNotExist)

    def test_create_legal_user(self):
        user = LegalUser.new_user(
            company_code=CompanyCodeField('1'*11),
            phone_number=PhoneNumberField('1'*10),
            company_name='test',
            domain='test',
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        db_user = self.database.users.create(user)

        assert db_user == user

    def test_create_already_exist_legal_user(self):
        user = LegalUser.new_user(
            company_code=CompanyCodeField('1'*11),
            phone_number=PhoneNumberField('1'*10),
            company_name='test',
            domain='test',
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        db_user = self.database.users.create(user)

        with self.assertRaises(errors.UserAlreadyExist):
            self.database.users.create(user)

    def test_create_legal_user_with_none_existent_platform(self):
        user = LegalUser.new_user(
            company_code=CompanyCodeField('1'*11),
            phone_number=PhoneNumberField('1'*10),
            company_name='test',
            domain='test',
            plain_password='plain_password',
            roles=[
                UserRole(platform='invalid', names=['admin'])
            ],
        )

        try:
            self.database.users.create(user)
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.RoleDoesNotExist)

    def test_create_legal_user_with_invalid_province(self):
        user = LegalUser.new_user(
            company_code=CompanyCodeField('1'*11),
            phone_number=PhoneNumberField('1'*10),
            company_name='test',
            domain='test',
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        user.contact_information = ContactInformation(
            city_id=ObjectIdField(ObjectId()))  # type: ignore

        try:
            self.database.users.create(user)
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.CityDoesNotExist)

    def test_get_legal_user_by_company_code(self):
        user = LegalUser.new_user(
            company_code=CompanyCodeField('1'*11),
            phone_number=PhoneNumberField('1'*10),
            company_name='test',
            domain='test',
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.database.users.create(user)

        db_user = self.database.users.get_by_company_code(
            CompanyCodeField(user.company_code))

        self.assertEqual(db_user, user)

    def test_get_none_existent_user(self):
        user = LegalUser.new_user(
            company_code=CompanyCodeField('1'*11),
            phone_number=PhoneNumberField('1'*10),
            company_name='test',
            domain='test',
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.database.users.create(user)

        try:
            self.database.users.get_by_company_code(
                CompanyCodeField('2'*11))
            assert False
        except Exception as exc:
            assert isinstance(exc, errors.UserDoesNotExist)

    def test_update_last_login(self):
        user = LegalUser.new_user(
            company_code=CompanyCodeField('1'*11),
            phone_number=PhoneNumberField('1'*10),
            company_name='test',
            domain='test',
            plain_password='plain_password',
            roles=[
                UserRole(platform='*', names=['admin'])
            ],
        )
        self.database.users.create(user)
        self.database.users.update_last_login(user)
        db_user = self.database.users.get_by_id(str(user.id))
        assert db_user.last_login > user.last_login
