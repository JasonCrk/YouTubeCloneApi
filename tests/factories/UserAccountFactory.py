import factory

from apps.user.models import UserAccount

from tests.constants import TEST_PASSWORD


class BaseUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserAccount

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    password = TEST_PASSWORD


class UserFactory(BaseUserFactory):
    class Meta:
        model = UserAccount

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> UserAccount:
        manage = cls._get_manager(model_class)
        return manage.create_user(*args, **kwargs)


class AdminFactory(BaseUserFactory):
    class Meta:
        model = UserAccount

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> UserAccount:
        manage = cls._get_manager(model_class)
        return manage.create_superuser(*args, **kwargs)
