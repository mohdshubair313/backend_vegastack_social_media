from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    # Always show follower & following info in nested form
    follower = serializers.PrimaryKeyRelatedField(read_only=True)
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    following_username = serializers.CharField(source='following.username', read_only=True)

    class Meta:
        model = Follow
        fields = [
            'id',
            'follower', 'follower_username',
            'following', 'following_username',
            'created_at'
        ]
        read_only_fields = ['id', 'follower', 'created_at', 'follower_username', 'following_username']

    def validate_following(self, value):
        """
        Prevent self-follow.
        """
        request = self.context.get('request')
        if request and request.user == value:
            raise serializers.ValidationError("You cannot follow yourself.")
        return value

    def create(self, validated_data):
        """
        Ensure follower is always request.user.
        """
        request = self.context.get('request')
        if request:
            validated_data['follower'] = request.user
        return super().create(validated_data)


class UserSummarySerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='profile.followers_count', read_only=True)
    following_count = serializers.IntegerField(source='profile.following_count', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'followers_count', 'following_count']
