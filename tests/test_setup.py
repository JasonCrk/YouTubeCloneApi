from rest_framework.test import APITestCase

from apps.user.models import UserAccount

from tests.factories.user_account_factory import AdminFactory
from tests.constants import TEST_PASSWORD


class TestSetup(APITestCase):
    def setUp(self):
        create_jwt_url = '/api/auth/jwt/create'

        self.user: UserAccount = AdminFactory.create()

        response = self.client.post(
            create_jwt_url,
            {
                'email': self.user.email,
                'password': TEST_PASSWORD
            },
            format='json'
        )

        self.access_token: str = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        return super().setUp()
