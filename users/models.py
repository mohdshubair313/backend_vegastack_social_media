from django.conf import settings
from django.db import models
from django.utils import timezone

PRIVACY_CHOICES = (
    ('public', 'Public'),
    ('private', 'Private'),
    ('followers', 'Followers Only'),
)

def avatar_upload_to(instance, filename):
    # local storage path: media/avatars/user_<id>/<filename>
    return f'avatars/user_{instance.user.id}/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.CharField(max_length=160, blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)  # canonical public URL (Supabase or local)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')

    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'User profiles'

    def __str__(self):
        return f'Profile: {self.user}'
