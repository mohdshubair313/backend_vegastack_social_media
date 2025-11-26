from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Like, Comment
from posts.models import Post

@receiver(post_save, sender=Like)
def update_like_count_on_save(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        post.like_count = Like.objects.filter(post=post).count()
        post.save(update_fields=['like_count'])

@receiver(post_delete, sender=Like)
def update_like_count_on_delete(sender, instance, **kwargs):
    post = instance.post
    post.like_count = Like.objects.filter(post=post).count()
    post.save(update_fields=['like_count'])

@receiver(post_save, sender=Comment)
def update_comment_count_on_save(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        post.comment_count = Comment.objects.filter(post=post).count()
        post.save(update_fields=['comment_count'])

@receiver(post_delete, sender=Comment)
def update_comment_count_on_delete(sender, instance, **kwargs):
    post = instance.post
    post.comment_count = Comment.objects.filter(post=post).count()
    post.save(update_fields=['comment_count'])
