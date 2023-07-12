# Generated by Django 4.2.2 on 2023-07-12 14:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner', models.URLField(blank=True, null=True, verbose_name='Banner image URL')),
                ('picture', models.URLField(blank=True, null=True, verbose_name='Avatar image URL')),
                ('description', models.TextField(blank=True, null=True)),
                ('joined', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=25, verbose_name='channel name')),
                ('handle', models.CharField(blank=True, max_length=28, unique=True)),
                ('contact_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Contact email')),
            ],
        ),
        migrations.CreateModel(
            name='ChannelSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_date', models.DateTimeField(auto_now_add=True)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='channel.channel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='channel',
            name='subscription',
            field=models.ManyToManyField(related_name='channel_subscription', through='channel.ChannelSubscription', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='channel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
