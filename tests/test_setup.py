from django.http import HttpResponse

from rest_framework.test import APITestCase
from rest_framework import status

from faker import Faker

class TestSetup(APITestCase):
    def setUp(self):
        from apps.user.models import UserAccount

        faker = Faker()

        self.create_jwt_url = '/api/auth/jwt/create'

        self.user = UserAccount.objects.create_superuser(
            username=faker.name(),
            email=faker.email(),
            first_name='Account',
            last_name='Test',
            password='AccountTestPassword'
        )

        response: HttpResponse = self.client.post(
            self.create_jwt_url,
            {
                'email': self.user.email,
                'password': 'AccountTestPassword'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.access_token: str = response.data['access'] # type: ignore
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}') # type: ignore

        return super().setUp()
