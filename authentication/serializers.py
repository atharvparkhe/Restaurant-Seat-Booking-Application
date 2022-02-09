from rest_framework import serializers
from authentication.models import SellerModel
from base.validators import validate_name

class loginSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True)

class signupSerializer(serializers.Serializer):
    name = serializers.CharField(required = True)
    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True)
    def validate(self, data):
        validate_name(data["name"])
        return data

class sellerSignupSerializer(serializers.Serializer):
    name = serializers.CharField(required = True)
    email = serializers.EmailField(required = True)
    phone = serializers.CharField(required = True)
    password = serializers.CharField(required = True)
    aadhar = serializers.CharField(required = True)
    gst = serializers.CharField(required = True)

class otpSerializer(serializers.Serializer):
    otp = serializers.IntegerField(required = True)
    npw = serializers.CharField(required = False)
    cpw = serializers.CharField(required = False)

class emailSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True)

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerModel
        fields = ["name", "email"]