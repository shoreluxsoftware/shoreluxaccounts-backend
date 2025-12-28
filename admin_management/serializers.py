from rest_framework import serializers
from .models import OTPVerification
from django.contrib.auth import authenticate

class OTPRequestSerializer(serializers.Serializer):
    verification_type = serializers.ChoiceField(choices=[
        'booking_edit', 'expense_edit', 'sales_income_edit', 'other_income_edit'
    ])
    object_id = serializers.IntegerField(required=False, allow_null=True)

class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, min_length=6)
    verification_type = serializers.ChoiceField(choices=[
        'booking_edit', 'expense_edit', 'sales_income_edit', 'other_income_edit'
    ])


    ############## serializers.py #################

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get("username"),
            password=data.get("password")
        )
        if not user:
            raise serializers.ValidationError("Invalid username or password")

        data["user"] = user
        return data