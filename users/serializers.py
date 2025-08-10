from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile
from .utils import validate_image_file, save_avatar_locally

User = get_user_model()

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # adjust fields as per your custom user

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    avatar = serializers.ImageField(write_only=True, required=False, allow_null=True)
    avatar_url = serializers.CharField(read_only=True)

    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'bio', 'avatar', 'avatar_url', 'website', 'location',
            'privacy', 'followers_count', 'following_count', 'posts_count'
        ]

    def validate_bio(self, value):
        if value and len(value) > 160:
            raise serializers.ValidationError('Bio must be 160 characters or less.')
        return value

    def update(self, instance, validated_data):
        # handle avatar separately
        avatar_file = validated_data.pop('avatar', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if avatar_file:
            # validate
            validate_image_file(avatar_file)
            # upload locally (or to Supabase)
            try:
                url = save_avatar_locally(avatar_file, instance.user)
                instance.avatar_url = url
                # Also save the file into ImageField (keeps local copy)
                # Rewind file and assign to instance.avatar
                avatar_file.seek(0)
                instance.avatar.save(avatar_file.name, avatar_file, save=False)
            except Exception as e:
                raise serializers.ValidationError({'avatar': str(e)})

        instance.save()
        return instance
