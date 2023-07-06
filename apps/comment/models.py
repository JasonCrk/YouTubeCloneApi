from django.db import models

from apps.user_profile.models import Profile
from apps.video.models import Video

class Comment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comment_profile')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comment_video')
    comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='comment_comment')
    content = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True, blank=True)
    was_edited = models.BooleanField(default=False)
    likes = models.ManyToManyField(Profile, through='LikedComment', related_name='comment_likes')

    class Meta:
        ordering = ['publication_date']

    def __str__(self) -> str:
        return self.profile.user.username

class LikedComment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    liked = models.BooleanField(default=True, blank=True)

    def __str__(self) -> str:
        return self.profile.user.username