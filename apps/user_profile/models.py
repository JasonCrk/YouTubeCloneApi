from django.db import models
from django.conf import settings

from .themes import THEMES
from .languages import LANGUAGES

User = settings.AUTH_USER_MODEL

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    picture = models.URLField(verbose_name='Picture or Avatar', null=True, blank=True)
    theme = models.CharField(choices=THEMES, default='light')
    languages = models.CharField(choices=LANGUAGES, default='EN')

    def __str__(self) -> str:
        return self.user.username