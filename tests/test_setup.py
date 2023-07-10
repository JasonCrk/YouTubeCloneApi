from django.http import HttpResponse

from rest_framework.test import APITestCase

from faker import Faker

class TestSetup(APITestCase):
    def setUp(self):
        from apps.user.models import UserAccount

        faker = Faker()

        self.create_jwt_url = '/api/auth/jwt/create'

        self.user = UserAccount.objects.create_superuser(
            username='TestMan',
            email=faker.email(),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
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

        self.access_token: str = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        return super().setUp()
