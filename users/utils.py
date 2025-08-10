from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from urllib.parse import urljoin

def validate_image_file(file_obj):
    # file_obj is InMemoryUploadedFile or similar
    content_type = getattr(file_obj, 'content_type', '')
    if content_type not in ('image/jpeg', 'image/png'):
        raise ValueError('Invalid image type. Only JPEG and PNG are allowed.')
    if file_obj.size > 2 * 1024 * 1024:
        raise ValueError('Image too large. Max 2MB allowed.')

def save_avatar_locally(file_obj, user):
    """
    Save file to default storage (MEDIA_ROOT) and return absolute URL.
    """
    path = f'avatars/user_{user.id}/{file_obj.name}'
    saved_path = default_storage.save(path, ContentFile(file_obj.read()))
    # build absolute url
    base = getattr(settings, 'SITE_BASE_URL', None)
    if base:
        return urljoin(base, settings.MEDIA_URL + saved_path)
    # fallback: return relative MEDIA_URL path
    return settings.MEDIA_URL + saved_path

# Optional: Supabase upload - requires supabase-py or requests and config in settings.
# This snippet is a starting point; install supabase client and set SUPABASE_URL / SUPABASE_KEY in settings.
def upload_avatar_to_supabase(file_obj, user):
    supabase_url = getattr(settings, 'SUPABASE_URL', None)
    supabase_key = getattr(settings, 'SUPABASE_KEY', None)
    if not supabase_url or not supabase_key:
        raise RuntimeError('Supabase config not set')

    from supabase import create_client, Client
    
    supabase:Client = create_client(supabase_url, supabase_key)

    bucket_name = "avator-images"
    path = f'user_{user.id}/{file_obj.name}'
    # file_obj must be bytes
    path = f'user_{user.id}/{file_obj.name}'
    file_obj.seek(0)
    file_bytes = file_obj.read()
    response = (
        supabase.storage
        .from_("avator-images")
        .upload(
            path=path,
            file=file_bytes,
        )
    )
    # Check for upload failure based on error attribute
    if getattr(response, "error", None) is not None:
        raise RuntimeError(f"Supabase upload failed: {getattr(response, 'error', response)}")
    public_url_response = supabase.storage.from_("avator-images").get_public_url(path)
    return public_url_response
