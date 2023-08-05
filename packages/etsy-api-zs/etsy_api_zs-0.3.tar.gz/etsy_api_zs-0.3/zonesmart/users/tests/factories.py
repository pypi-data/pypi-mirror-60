from django.contrib.auth import get_user_model

from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    first_name = "John"
    last_name = "Doe"
    email = "john_doe@zonesmart.ru"
    password = "secret"
    is_staff = False

    class Meta:
        model = User
        django_get_or_create = ["email"]


class AdminFactory(DjangoModelFactory):
    first_name = "Admin"
    last_name = "Adminov"
    email = "admin@zonesmart.ru"
    password = "4815162342"
    is_staff = True

    class Meta:
        model = User
        django_get_or_create = ["email"]
