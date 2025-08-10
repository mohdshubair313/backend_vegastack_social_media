from django.db import models
from django.conf import settings

POST_CATEGORIES = (
    ('general', 'General'),
    ('announcement', 'Announcement'),
    ('question', 'Question'),
)

def post_image_upload_path(instance, filename):
    return f'posts/user_{instance.author.id}/{filename}'

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField(max_length=280, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Public URL (Supabase or MEDIA)
    image_url = models.URLField(blank=True, null=True)

    # Optional local copy (MEDIA_ROOT)
    image = models.ImageField(upload_to=post_image_upload_path, blank=True, null=True)

    category = models.CharField(max_length=20, choices=POST_CATEGORIES, default='general')
    is_active = models.BooleanField(default=True)

    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Post {self.id} by {self.author}'
