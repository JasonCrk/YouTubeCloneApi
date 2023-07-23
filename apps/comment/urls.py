from django.urls import path

from apps.comment import views

urlpatterns = [
    path('create/<int:video_id>', views.CreateVideoCommentView.as_view(), name='create_video_comment')
]