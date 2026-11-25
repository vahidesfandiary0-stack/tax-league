import re
from rest_framework import serializers
from .models import User


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        normalized = re.sub(r"[\s()-]", "", value)
        if not re.fullmatch(r"\+?[0-9]{8,15}", normalized):
            raise serializers.ValidationError("شماره تلفن معتبر نیست.")
        return normalized


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    code = serializers.RegexField(r"^[0-9]{6}$")
    province = serializers.ChoiceField(choices=[value for value, _ in User.PROVINCE_CHOICES], required=False)
