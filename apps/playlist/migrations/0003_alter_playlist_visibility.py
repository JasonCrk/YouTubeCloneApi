# Generated by Django 4.2.2 on 2023-08-07 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0002_alter_playlist_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='visibility',
            field=models.CharField(choices=[('PUB', 'public'), ('PRI', 'private'), ('URL', 'only_url')], default='PUB', max_length=3),
        ),
    ]
