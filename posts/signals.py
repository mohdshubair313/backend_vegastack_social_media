from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Post

@receiver(post_save, sender=Post)
def update_user_posts_count_on_save(sender, instance, created, **kwargs):
    """
    Update the author's profile posts_count whenever a Post is created or updated.
    """
    profile = getattr(instance.author, 'profile', None)
    if profile:
        # Count only active posts if required, else remove filter
        profile.posts_count = Post.objects.filter(author=instance.author).count()
        profile.save(update_fields=['posts_count'])

@receiver(post_delete, sender=Post)
def update_user_posts_count_on_delete(sender, instance, **kwargs):
    """
    Update the author's profile posts_count whenever a Post is deleted.
    """
    profile = getattr(instance.author, 'profile', None)
    if profile:
        profile.posts_count = Post.objects.filter(author=instance.author).count()
        profile.save(update_fields=['posts_count'])
