from django.db.models import TextChoices

class Visibility(TextChoices):
    PUBLIC = 'PUB', 'public'
    PRIVATE = 'PRI', 'private'
    ONLY_URL = 'URL', 'only_url'
