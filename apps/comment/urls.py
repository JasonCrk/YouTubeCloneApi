from django.urls import path

from apps.comment import views

urlpatterns = [
    path(
        'video/<int:video_id>/',
        views.RetrieveVideoCommentsView.as_view(),
        name='video_comments'
    ),
    path(
        'comment/<int:comment_id>/',
        views.RetrieveCommentsOfCommentView.as_view(),
        name='comments_of_comment'
    ),
    path(
        'video/<int:video_id>/create/',
        views.CreateVideoCommentView.as_view(),
        name='create_video_comment'
    ),
    path(
        'comment/<int:comment_id>/create/',
        views.CreateCommentForCommentView.as_view(),
        name='create_comment_for_comment'
    ),
    path(
        '<int:comment_id>/like/',
        views.LikeCommentView.as_view(),
        name='like_comment'
    ),
    path(
        '<int:comment_id>/dislike/',
        views.DislikeCommentView.as_view(),
        name='dislike_comment'
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