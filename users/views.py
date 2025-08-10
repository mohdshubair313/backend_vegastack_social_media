from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import UserProfile
from .serializers import UserProfileSerializer
from .permissions import IsOwnerOrAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileDetailView(generics.RetrieveAPIView):
    """
    GET /api/users/{user_id}/
    Shows profile depending on privacy settings.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]  # check privacy inside

    def get_object(self):
        user_id = self.kwargs.get('user_id')  # expects key user_id in url
        user = get_object_or_404(User, id=user_id)
        profile = getattr(user, 'profile', None)
        if not profile:
            # If profile missing (shouldn't happen), create one
            from .models import UserProfile
            profile = UserProfile.objects.create(user=user)
        return profile

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        # privacy logic
        if profile.privacy == 'public' or request.user.is_staff:
            return super().retrieve(request, *args, **kwargs)

        if request.user.is_authenticated:
            # owner can view
            if request.user == profile.user:
                return super().retrieve(request, *args, **kwargs)

            # if privacy = 'followers', check follow relation
            if profile.privacy == 'followers':
                # check follows app: does request.user follow profile.user ?
                from django.apps import apps
                Follow = apps.get_model('follows', 'Follow')
                follows = Follow.objects.filter(follower=request.user, following=profile.user).exists()
                if follows:
                    return super().retrieve(request, *args, **kwargs)
                return Response({'detail': 'Profile visible to followers only.'}, status=status.HTTP_403_FORBIDDEN)

            # private
            return Response({'detail': 'Profile is private.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # anonymous
            return Response({'detail': 'Login required to view this profile.'}, status=status.HTTP_401_UNAUTHORIZED)


class UserMeUpdateView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/users/me/
    Update your own profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            from .models import UserProfile
            profile = UserProfile.objects.create(user=self.request.user)
        return profile


class UsersListView(generics.ListAPIView):
    """
    GET /api/users/?q=search
    - Admin: return all users with profile
    - Non-admin: only search by 'q' param; returns public profiles and 'followers' (if requester follows them)
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]  # additional checks below
    pagination_class = None  # use default or set PageNumberPagination

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        if self.request.user and self.request.user.is_staff:
            # admin: return all profiles, optionally filter by q
            qs = UserProfile.objects.select_related('user').all()
            if q:
                qs = qs.filter(
                    Q(user__username__icontains=q) |
                    Q(user__email__icontains=q) |
                    Q(bio__icontains=q)
                )
            return qs

        # non-admin: must provide q to search; otherwise error handled in list()
        if not q:
            return UserProfile.objects.none()

        # return public profiles and those followers-only where request.user follows them
        public_qs = UserProfile.objects.filter(privacy='public').filter(
            Q(user__username__icontains=q) |
            Q(user__email__icontains=q) |
            Q(bio__icontains=q)
        )

        followers_qs = UserProfile.objects.none()
        if self.request.user.is_authenticated:
            from django.apps import apps
            Follow = apps.get_model('follows', 'Follow')
            # get ids of users that request.user follows
            following_ids = Follow.objects.filter(follower=self.request.user).values_list('following_id', flat=True)
            followers_qs = UserProfile.objects.filter(user_id__in=following_ids, privacy='followers').filter(
                Q(user__username__icontains=q) |
                Q(user__email__icontains=q) |
                Q(bio__icontains=q)
            )

        return (public_qs | followers_qs).distinct()

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff and not request.query_params.get('q'):
            return Response({'detail': 'Only admin can list all users. Non-admin must use ?q=search'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)
