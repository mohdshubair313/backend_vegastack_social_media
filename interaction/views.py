from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import F
from django.contrib.auth import get_user_model
from posts.models import Post
from .models import Like, Comment
from .serializers import LikeSerializer, CommentSerializer

User = get_user_model()

class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id, is_active=True)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({"detail":"Already liked."}, status=status.HTTP_200_OK)

        # atomic increment
        Post.objects.filter(pk=post.pk).update(like_count=F('like_count') + 1)

        # optional: create notification for post.author
        return Response({"detail":"Liked."}, status=status.HTTP_201_CREATED)

class UnlikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def delete(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        if deleted == 0:
            return Response({"detail":"Like not found."}, status=status.HTTP_404_NOT_FOUND)

        Post.objects.filter(pk=post.pk).update(like_count=F('like_count') - 1)
        return Response(status=status.HTTP_204_NO_CONTENT)

class LikeStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, post_id):
        liked = Like.objects.filter(user=request.user, post_id=post_id).exists()
        return Response({"liked": liked})

#comments section

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'], is_active=True)
        comment = serializer.save(user=self.request.user, post=post)
        Post.objects.filter(pk=post.pk).update(comment_count=F('comment_count') + 1)
        return comment


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # or set PageNumberPagination

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id, is_active=True).order_by('-created_at')

class CommentDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.user != request.user and not request.user.is_staff:
            return Response({"detail":"Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        with transaction.atomic():
            comment.is_active = False
            comment.save(update_fields=['is_active'])
            Post.objects.filter(pk=comment.post.id).update(comment_count=F('comment_count') - 1)
        return Response(status=status.HTTP_204_NO_CONTENT)
