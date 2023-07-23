from django.urls import path

from apps.comment import views

urlpatterns = [
    path(
        'create/<int:video_id>/',
        views.CreateVideoCommentView.as_view(),
        name='create_video_comment'
    ),
    path(
        '<int:comment_id>/create/',
        views.CreateCommentForCommentView.as_view(),
        name='create_comment_for_comment'
    )
]