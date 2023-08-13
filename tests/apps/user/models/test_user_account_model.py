from django.test import TestCase

from tests.factories.user_account import UserFactory

from apps.user.models import UserAccount


class TestUserAccountModel(TestCase):
    def setUp(self):
        self.user_account: UserAccount = UserFactory.create()

    def test_the_str_returns_the_username(self):
        """
        Should verify if the __str__ method returns
        the username of user account
        """
        self.assertEqual(self.user_account.__str__(), self.user_account.username)

    def test_user_account_has_been_created(self):
        """
        Should verify if the user account has been created
        """
        user_account = UserAccount.objects.filter(id=self.user_account.pk)
        self.assertTrue(user_account.exists())

    def test_USERNAME_FIELD_is_the_email(self):
        """
        Should verify if the USERNAME_FIELD property is equal to 'email' 
        """
        self.assertEqual(self.user_account.USERNAME_FIELD, 'email')

    def test_REQUIRED_FIELDS_attribute(self):
        """
        Should verify if the REQUIRE_FIELDS property contains 'username', 'first_name' and 'last_name' 
        """
        self.assertIn('username', self.user_account.REQUIRED_FIELDS)
        self.assertIn('first_name', self.user_account.REQUIRED_FIELDS)
        self.assertIn('last_name', self.user_account.REQUIRED_FIELDS)

    def test_get_full_name_method(self):
        """
        Should verify if the get_full_name method returns
        the full name of user account
        """
        full_name = self.user_account.first_name + ' ' + self.user_account.last_name
        self.assertEqual(self.user_account.get_full_name(), full_name)

    def test_is_staff_property_equals_is_admin_property(self):
        """
        Should verify if the is_staff property is equals to the is_admin property
        """
        self.assertEqual(self.user_account.is_staff, self.user_account.is_admin)
