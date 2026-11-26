import re
from rest_framework import serializers


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


class ProfileSerializer(serializers.Serializer):
    display_name = serializers.CharField(max_length=80, trim_whitespace=True)

    def validate_display_name(self, value):
        parts = value.split()
        if len(parts) < 2:
            raise serializers.ValidationError("نام و نام خانوادگی را کامل وارد کنید.")
        if any(len(part) < 2 for part in parts):
            raise serializers.ValidationError("نام و نام خانوادگی باید معتبر باشند.")
        return " ".join(parts)
