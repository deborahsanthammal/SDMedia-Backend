from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from .models import userProfile


class userProfileSerializer(ModelSerializer):
    class Meta:
        model = userProfile
        fields = [
            "profile_picture",
            "bio",
        ]

class UserSerializer(ModelSerializer):

    user_profile = userProfileSerializer("user_profile", read_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "user_profile"
        ]