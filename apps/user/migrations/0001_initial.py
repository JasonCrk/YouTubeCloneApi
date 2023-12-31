# Generated by Django 4.2.2 on 2023-07-12 14:39

import apps.user.models
import apps.user.validations
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=150, unique=True, verbose_name='user e-mail')),
                ('username', models.CharField(max_length=25)),
                ('first_name', models.CharField(max_length=25, verbose_name='user first name')),
                ('last_name', models.CharField(max_length=25, verbose_name='user last name')),
                ('phone_number', models.PositiveIntegerField(blank=True, null=True, unique=True, validators=[apps.user.validations.validate_phone_number])),
                ('language', models.CharField(choices=[('ES', 'Spanish'), ('EN', 'English')], default='EN')),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'Dark')], default='light')),
                ('id_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', apps.user.models.UserAccountManager()),
            ],
        ),
    ]
