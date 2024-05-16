from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import ModelSerializer, CharField
from .models import CustomUser


class RegisterSerializer(ModelSerializer):
    password = CharField(validators=[validate_password])

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    class Meta:
        model = CustomUser
        fields = ['email', 'password']


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'birth_date', 'phone_number', 'avatar']
