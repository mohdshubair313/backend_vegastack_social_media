# posts/serializers.py
from rest_framework import serializers
from django.conf import settings
from .models import Post
from .utils import validate_image_file, save_image_locally, upload_image_to_supabase

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    image_url = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "content", "author", "created_at", "updated_at",
            "image", "image_url", "category", "is_active", "like_count", "comment_count"
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at", "image_url", "like_count", "comment_count"]

    def validate_content(self, value):
        if value and len(value) > 280:
            raise serializers.ValidationError("Content cannot exceed 280 characters.")
        return value

    def validate_image(self, image):
        if image is None:
            return image
        try:
            validate_image_file(image)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        return image

    def _handle_image_upload(self, post_obj, image_file, author):
        """
        Upload image either to Supabase (if configured) or local storage.
        Save image_url on post_obj and optionally store a local copy to ImageField.
        """
        try:
            if getattr(settings, "SUPABASE_URL", None) and getattr(settings, "SUPABASE_KEY", None):
                url = upload_image_to_supabase(image_file, author)
            else:
                url = save_image_locally(image_file, author, subpath="posts")

            post_obj.image_url = url

            # Save a local copy as well (rewind file and assign to ImageField) for admin/dev convenience
            try:
                image_file.seek(0)
                post_obj.image.save(image_file.name, image_file, save=False)
            except Exception:
                # If saving local ImageField fails, we still keep image_url (don't raise)
                pass

            post_obj.save(update_fields=["image_url", "image"])
        except Exception as exc:
            # propagate meaningful validation error to the API client
            raise serializers.ValidationError({"image": f"Failed to upload image: {str(exc)}"})

    def create(self, validated_data):
        # Pop image if present
        image_file = validated_data.pop("image", None)
        # Safely get author (may be provided via serializer.save(author=...))
        author = validated_data.pop("author", None)
        if author is None:
            # fallback to request user (if serializer context provided)
            author = getattr(self.context.get("request"), "user", None)

        # create the post without image_url first
        post = Post.objects.create(author=author, **validated_data)

        # handle image upload after post created (so we have post id)
        if image_file:
            try:
                self._handle_image_upload(post, image_file, author)
            except serializers.ValidationError:
                # delete post if upload failed to keep DB clean
                post.delete()
                raise

        return post

    def update(self, instance, validated_data):
        image_file = validated_data.pop("image", None)
        # author might be present in validated_data if caller passed it; prevent overwrite
        validated_data.pop("author", None)

        # update other fields
        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        if image_file:
            # handle replacing image (upload + update image_url)
            self._handle_image_upload(instance, image_file, getattr(instance, "author", None))

        instance.save()
        return instance
