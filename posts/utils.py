# posts/utils.py
import io
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from urllib.parse import urljoin

ALLOWED_CONTENT_TYPES = ('image/jpeg', 'image/png')
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB

def validate_image_file(file_obj):
    content_type = getattr(file_obj, 'content_type', '')
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError('Invalid image type. Only JPEG and PNG allowed.')
    if getattr(file_obj, 'size', 0) > MAX_IMAGE_SIZE:
        raise ValueError('Image too large. Max size is 2MB.')

def save_image_locally(file_obj, author, subpath='posts'):
    """
    Save to MEDIA_ROOT and return relative URL (MEDIA_URL + path)
    """
    filename = file_obj.name
    path = f'{subpath}/user_{author.id}/{filename}'
    saved_path = default_storage.save(path, ContentFile(file_obj.read()))
    base = getattr(settings, 'SITE_BASE_URL', None)
    if base:
        return urljoin(base, settings.MEDIA_URL + saved_path)
    return settings.MEDIA_URL + saved_path

# Supabase upload implementation (optional)
def upload_image_to_supabase(file_obj, author, bucket='posts'):
    """
    Uploads file_obj (InMemoryUploadedFile) to Supabase Storage and returns public URL.

    Requires SUPABASE_URL and SUPABASE_KEY in settings, and supabase-py or requests approach.
    This example uses requests to Supabase Storage REST API.

    NOTE: Using service_role key on server is required to upload. NEVER expose it to frontend.
    """
    supabase_url = getattr(settings, 'SUPABASE_URL', None)
    supabase_key = getattr(settings, 'SUPABASE_KEY', None)
    if not supabase_url or not supabase_key:
        raise RuntimeError('Supabase not configured.')

    import requests
    # Ensure bucket path
    filename = file_obj.name
    path = f'{bucket}/user_{author.id}/{filename}'
    file_obj.seek(0)
    headers = {
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': getattr(file_obj, 'content_type', 'application/octet-stream'),
    }
    upload_url = f'{supabase_url}/storage/v1/object/{path}'
    # Supabase REST expects /object/{bucket}/{path} normally; if using direct endpoint, adapt accordingly.
    # Using the Python client (supabase-py) is recommended; adjust as per your SDK.
    resp = requests.post(f'{supabase_url}/storage/v1/object/{bucket}/user_{author.id}/{filename}',
                         headers=headers, data=file_obj.read())
    if resp.status_code not in (200, 201):
        raise RuntimeError(f'Supabase upload failed: {resp.status_code} {resp.text}')
    # Get public url (adjust via Supabase REST or pattern)
    public_url = f'{supabase_url}/storage/v1/object/public/{bucket}/user_{author.id}/{filename}'
    return public_url
