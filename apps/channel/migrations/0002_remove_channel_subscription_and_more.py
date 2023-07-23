# Generated by Django 4.2.2 on 2023-07-15 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='subscription',
        ),
        migrations.RemoveField(
            model_name='channelsubscription',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='channelsubscription',
            name='user',
        ),
        migrations.AddField(
            model_name='channel',
            name='subscriptions',
            field=models.ManyToManyField(through='channel.ChannelSubscription', to='channel.channel'),
        ),
        migrations.AddField(
            model_name='channelsubscription',
            name='subscriber',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriber', to='channel.channel'),
        ),
        migrations.AddField(
            model_name='channelsubscription',
            name='subscribing',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscribing', to='channel.channel'),
        ),
    ]