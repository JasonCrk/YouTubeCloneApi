# Generated by Django 4.2.2 on 2023-07-15 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0002_remove_channel_subscription_and_more'),
        ('comment', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='likedcomment',
            name='user',
        ),
        migrations.AddField(
            model_name='comment',
            name='channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_channel', to='channel.channel'),
        ),
        migrations.AddField(
            model_name='likedcomment',
            name='channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='channel.channel'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_comment', to='comment.comment'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='likes',
            field=models.ManyToManyField(related_name='comment_likes', through='comment.LikedComment', to='channel.channel'),
        ),
    ]
