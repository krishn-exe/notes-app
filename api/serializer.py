from rest_framework import serializers
from django.contrib.auth.models import User
from .models import apiNotes


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class NoteSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(max_length=500, required=False, allow_blank=True, default='')

    class Meta:
        model = apiNotes
        fields = ['id', 'title', 'content', 'image_url', 'updated_at']
        read_only_fields = ['id', 'updated_at']
