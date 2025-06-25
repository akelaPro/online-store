from venv import logger
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreateSerializer(BaseUserCreateSerializer):
    def create(self, validated_data):
        logger.debug(f"Creating new user with email: {validated_data.get('email')}")
        try:
            if not validated_data.get('username'):
                validated_data['username'] = validated_data['email'].split('@')[0]
                logger.debug(f"Generated username: {validated_data['username']}")
            
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                username=validated_data['username']
            )
            logger.info(f"New user created: {user.username}")
            return user
        except Exception as e:
            logger.error(f"User creation failed: {str(e)}")
            raise serializers.ValidationError(str(e))