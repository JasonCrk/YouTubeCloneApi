from django.urls import path

from apps.comment import views

urlpatterns = [
    path(
        'like/',
        views.LikeCommentView.as_view(),
        name='like_comment'
    ),
    path(
        'dislike/',
        views.DislikeCommentView.as_view(),
        name='dislike_comment'
    ),
    path(
        'create/<int:video_id>/',
        views.CreateVideoCommentView.as_view(),
        name='create_video_comment'
    ),
    path(
        '<int:comment_id>/create/',
        views.CreateCommentForCommentView.as_view(),
        name='create_comment_for_comment'
    ),
    path(
        '<int:comment_id>/edit/',
        views.EditCommentView.as_view(),
        name='edit_comment'
    ),
    path(
        '<int:comment_id>/delete/',
        views.DeleteCommentView.as_view(),
        name='delete_comment'
    )
]