from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from apps.user_profile.models import Profile
from apps.channel.models import Channel

from apps.user.validations import validate_phone_number

class UserAccountManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, username, first_name, last_name, password=None, **entra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        user: UserAccount = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            **entra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        profile = Profile.objects.create(user=user)
        profile.save()

        channel = Channel.objects.create(handle=user.username, user_profile=profile)
        channel.save()

        return user

    def create_superuser(self, email, username, first_name, last_name, password=None, **entra_fields):
        user = self.create_user(
            email,
            username,
            first_name,
            last_name,
            password,
            **entra_fields
        )

        user.is_admin = True
        user.save(using=self._db)

        return user

class UserAccount(AbstractBaseUser):
    email = models.EmailField(verbose_name='user e-mail', unique=True, max_length=150)
    username = models.CharField(unique=True, max_length=20)
    first_name = models.CharField(verbose_name='user first name', max_length=25)
    last_name = models.CharField(verbose_name='user last name', max_length=25)
    phone_number = models.PositiveIntegerField(
        verbose_name='user phone number',
        validators=[validate_phone_number],
        unique=True,
        null=True,
        blank=True
    )
    id_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        return self.first_name + ' ' + self.last_name

    def has_perm(self, perm, obj=None) -> bool:
        return True
    
    def has_module_perms(self, app_label) -> bool:
        return True

    @property
    def is_staff(self) -> bool:
        return self.is_admin
