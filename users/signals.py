from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create profile when user is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from .models import UserProfile
        UserProfile.objects.create(user=instance)

# Update posts count when Post is created/deleted
@receiver(post_save)
def update_posts_count_on_create(sender, instance, created, **kwargs):
    app_label = getattr(sender, '__module__', '').split('.')[0]
    if app_label == 'posts' and sender.__name__ == 'Post':
        profile = getattr(instance.author, 'profile', None)
        if profile:
            profile.posts_count = sender.objects.filter(author=instance.author).count()
            profile.save(update_fields=['posts_count'])

@receiver(post_delete)
def update_posts_count_on_delete(sender, instance, **kwargs):
    app_label = getattr(sender, '__module__', '').split('.')[0]
    if app_label == 'posts' and sender.__name__ == 'Post':
        profile = getattr(instance.author, 'profile', None)
        if profile:
            profile.posts_count = sender.objects.filter(author=instance.author).count()
            profile.save(update_fields=['posts_count'])

# Update follower/following counters on follow create/delete
@receiver(post_save)
def update_follow_counts_on_create(sender, instance, created, **kwargs):
    app_label = getattr(sender, '__module__', '').split('.')[0]
    if app_label == 'follows' and sender.__name__ == 'Follow':
        if created:
            follower = getattr(instance, 'follower', None)
            following = getattr(instance, 'following', None)
            if follower and following:
                if hasattr(follower, 'profile'):
                    follower.profile.following_count = sender.objects.filter(follower=follower).count()
                    follower.profile.save(update_fields=['following_count'])
                if hasattr(following, 'profile'):
                    following.profile.followers_count = sender.objects.filter(following=following).count()
                    following.profile.save(update_fields=['followers_count'])

@receiver(post_delete)
def update_follow_counts_on_delete(sender, instance, **kwargs):
    app_label = getattr(sender, '__module__', '').split('.')[0]
    if app_label == 'follows' and sender.__name__ == 'Follow':
        follower = getattr(instance, 'follower', None)
        following = getattr(instance, 'following', None)
        if follower and hasattr(follower, 'profile'):
            follower.profile.following_count = sender.objects.filter(follower=follower).count()
            follower.profile.save(update_fields=['following_count'])
        if following and hasattr(following, 'profile'):
            following.profile.followers_count = sender.objects.filter(following=following).count()
            following.profile.save(update_fields=['followers_count'])
