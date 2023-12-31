# Generated by Django 4.2.2 on 2023-09-05 04:35

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0004_rename_banner_channel_banner_url_and_more'),
        ('video', '0006_alter_videoview_channel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videoview',
            name='channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_query_name='views', to='channel.channel'),
        ),
        migrations.AlterField(
            model_name='videoview',
            name='last_view_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 9, 5, 4, 35, 26, 331847, tzinfo=datetime.timezone.utc)),
        ),
    ]
