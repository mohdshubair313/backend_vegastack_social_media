from django.urls import path
from .views import (
    LikePostView, UnlikePostView, LikeStatusView,
    CommentCreateView, CommentListView, CommentDeleteView
)

urlpatterns = [
    path('posts/<int:post_id>/like/', LikePostView.as_view(), name='like-post'),
    path('posts/<int:post_id>/like-status/', LikeStatusView.as_view(), name='like-status'),
    path('posts/<int:post_id>/unlike/', UnlikePostView.as_view(), name='unlike-post'),
    path('posts/<int:post_id>/comments/', CommentListView.as_view(), name='comments-list'),
    path('posts/<int:post_id>/comments/create/', CommentCreateView.as_view(), name='comments-create'),
    path('comments/<int:comment_id>/', CommentDeleteView.as_view(), name='comment-delete'),
]
