# api/serializers.py
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import SpamReport, User, Contact
from django.contrib.auth.hashers import make_password, check_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'email', 'password']

    def create(self, validated_data):
        # Hash the password before saving the user
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Hash the new password if it is being updated
        if 'password' in validated_data:
            validated_data['password'] = make_password(
                validated_data['password'])
        return super().update(instance, validated_data)


# api/serializers.py
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'phone_number', 'email', 'password']

    def validate_phone_number(self, value):
        """Ensure that the phone number is unique."""
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        # Hash password before creating user
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


# api/serializers.py
class SpamNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact  # Use the Contact model if spam is being tracked for user contacts
        fields = ['phone_number', 'user', 'is_spam']


# class ContactSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Contact  # Link to the Contact model
#         # Fields to include in the API response
#         fields = ['id', 'name', 'phone_number', 'is_spam', 'user']


# api/serializers.py


class PhoneTokenObtainPairSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'No account found with given credentials.')

        if not check_password(password, user.password):
            raise serializers.ValidationError('Incorrect password.')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ContactSerializer(serializers.ModelSerializer):
    spam_likelihood = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone_number', 'spam_likelihood', 'user']

    def get_spam_likelihood(self, obj):
        total_reports = SpamReport.objects.filter(
            phone_number=obj.phone_number).count()
        total_users = User.objects.count()
        if total_users > 0:
            return total_reports / total_users
        return 0
