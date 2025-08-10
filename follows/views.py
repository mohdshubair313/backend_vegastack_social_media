from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from .models import Follow
from .serializers import FollowSerializer, UserSummarySerializer

User = get_user_model()


# Follow a user
class FollowUserView(generics.CreateAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)


# Unfollow a user
class UnfollowUserView(generics.DestroyAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        following_id = self.kwargs.get("user_id")
        return Follow.objects.get(follower=self.request.user, following_id=following_id)


# List all followers of a user
class FollowersListView(generics.ListAPIView):
    serializer_class = UserSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return User.objects.filter(following__following_id=user_id)


# List all users the given user is following
class FollowingListView(generics.ListAPIView):
    serializer_class = UserSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return User.objects.filter(follower__follower_id=user_id)
