from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.models import RestaurantModel
from .models import *
from .threads import *
from .serializers import *


@api_view(["POST"])
def signUp(request):
    try:
        data = request.data
        serializer = signupSerializer(data=data)
        if serializer.is_valid():
            name = serializer.data["name"]
            email = serializer.data["email"]
            password = serializer.data["password"]
            if CustomerModel.objects.filter(email=email).first():
                return Response({"message":"Acount already exists."}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                new_customer = CustomerModel.objects.create(email=email, name=name)
                new_customer.set_password(password)
                thread_obj = send_verification_email(email)
                thread_obj.start()
                new_customer.save()
                return Response({"message":"Account created, verification mail sent"}, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def verify(request):
    try:
        data = request.data
        serializer = otpSerializer(data=data)
        if serializer.is_valid():
            otp = serializer.data["otp"]
            if not OTPModel.objects.filter(otp=otp).first():
                return Response({"message":"OTP expired"}, status=status.HTTP_408_REQUEST_TIMEOUT)
            otp_obj = OTPModel.objects.get(otp=otp)
            if otp_obj.is_valid == False:
                return Response({"message":"OTP expired"}, status=status.HTTP_408_REQUEST_TIMEOUT)
            user_obj = CustomerModel.objects.filter(email=otp_obj.user.email).first()
            if user_obj:
                if user_obj.is_verified:
                    return Response({"message":"Account is already verified"}, status=status.HTTP_412_PRECONDITION_FAILED)
                user_obj.is_verified = True
                user_obj.save()
                return Response({"message":"Account verification successfull"}, status=status.HTTP_202_ACCEPTED)
            return Response({"message":"Account does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def logIn(request):
    try:
        data = request.data
        serializer = loginSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data["email"]
            password = serializer.data["password"]
            customer_obj = CustomerModel.objects.filter(email=email).first()
            if customer_obj is None:
                return Response({"message":"Account does not exist"}, status=status.HTTP_404_NOT_FOUND)
            if not customer_obj.is_verified:
                return Response({"message":"Email not verified. Check your mail"}, status=status.HTTP_401_UNAUTHORIZED)
            user = authenticate(email=email, password=password)
            if not user:
                return Response({"message":"Incorrect password"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            jwt_token = RefreshToken.for_user(user)
            return Response({"message":"Login successfull", "token":str(jwt_token.access_token)}, status=status.HTTP_202_ACCEPTED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def forgot(request):
    try:
        data = request.data
        serializer = emailSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data["email"]
            if not CustomerModel.objects.get(email=email):
                return Response({"message":"Account does not exists"}, status=status.HTTP_404_NOT_FOUND)
            thread_obj = send_forgot_link(email)
            thread_obj.start()
            return Response({"message":"reset mail sent"}, status=status.HTTP_200_OK)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def reset(request):
    try:
        data = request.data
        serializer = otpSerializer(data=data)
        if serializer.is_valid():
            otp = serializer.data["otp"]
            if not OTPModel.objects.filter(otp=otp).first():
                return Response({"message":"OTP expired"}, status=status.HTTP_408_REQUEST_TIMEOUT)
            otp_obj = OTPModel.objects.get(otp=otp)
            if otp_obj.is_valid == False:
                return Response({"message":"OTP expired"}, status=status.HTTP_408_REQUEST_TIMEOUT)
            if not CustomerModel.objects.filter(email=otp_obj.user.email).first():
                return Response({"message":"user does not exist"}, status=status.HTTP_404_NOT_FOUND)
            user_obj = CustomerModel.objects.get(email=otp_obj.user.email)
            npw = serializer.data["npw"]
            cpw = serializer.data["cpw"]
            if npw == cpw:
                user_obj.set_password(cpw)
                user_obj.save()
                return Response({"message":"Password changed successfull"}, status=status.HTTP_202_ACCEPTED)
        else:return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def resendForgot(request):
    try:
        data = request.data
        serializer = emailSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data["email"]
            thread_obj = send_forgot_link(email)
            thread_obj.start()
            return Response({"message":"OTP sent on your email"}, status=status.HTTP_200_OK)
        return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def resendVerify(request):
    try:
        data = request.data
        serializer = emailSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data["email"]
            obj = CustomerModel.objects.get(email=email)
            if obj.is_verified == True:
                return Response({"message":"Account already verified"}, status=status.HTTP_208_ALREADY_REPORTED)
            thread_obj = send_verification_email(email)
            thread_obj.start()
            return Response({"message":"OTP sent on your email"}, status=status.HTTP_200_OK)
        return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###############################################################################################################

@api_view(["POST"])
def sellerSignUp(request):
    try:
        data = request.data
        serializer = sellerSignupSerializer(data=data)
        if serializer.is_valid():
            name = serializer.data["name"]
            email = serializer.data["email"]
            phone = serializer.data["phone"]
            password = serializer.data["password"]
            gst = serializer.data["gst"]
            if SellerModel.objects.filter(email=email).first():
                return Response({"message":"Acount already exists."}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                new_seller = SellerModel.objects.create(email=email, name=name, gst_number=gst, phone=phone)
                new_seller.set_password(password)
                thread_obj = send_verification_email_seller(email)
                thread_obj.start()
                new_seller.save()
                return Response({"message":"Account created, verification mail sent"}, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def sellerVerify(request):
    try:
        data = request.data
        serializer = otpSerializer(data=data)
        if serializer.is_valid():
            otp = serializer.data["otp"]
            if not SellerOTP.objects.filter(otp=otp).first():
                return Response({"message":"OTP expired"}, status=status.HTTP_408_REQUEST_TIMEOUT)
            otp_obj = SellerOTP.objects.get(otp=otp)
            if otp_obj.is_valid == False:
                return Response({"message":"OTP expired"}, status=status.HTTP_408_REQUEST_TIMEOUT)
            user_obj = SellerModel.objects.filter(email=otp_obj.user.email).first()
            if user_obj:
                if user_obj.is_verified:
                    return Response({"message":"Account is already verified"}, status=status.HTTP_412_PRECONDITION_FAILED)
                user_obj.is_verified = True
                user_obj.save()
                return Response({"message":"Account verification successfull"}, status=status.HTTP_202_ACCEPTED)
            return Response({"message":"Account does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def sellerLogIn(request):
    try:
        data = request.data
        serializer = loginSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data["email"]
            password = serializer.data["password"]
            seller_obj = SellerModel.objects.filter(email=email).first()
            if seller_obj is None:
                return Response({"message":"Account does not exist"}, status=status.HTTP_404_NOT_FOUND)
            if not seller_obj.is_verified:
                return Response({"message":"Email not verified. Check your mail"}, status=status.HTTP_401_UNAUTHORIZED)
            user = authenticate(email=email, password=password)
            if not user:
                return Response({"message":"Incorrect password"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            jwt_token = RefreshToken.for_user(user)
            if RestaurantModel.objects.filter(owner=SellerModel.objects.get(email=email)):
                obj = RestaurantModel.objects.get(owner=SellerModel.objects.get(email=email))
                return Response({"message":"Login successfull", "token":str(jwt_token.access_token), "restaurant_id":obj.id}, status=status.HTTP_202_ACCEPTED)
            return Response({"message":"Login successfull", "token":str(jwt_token.access_token)}, status=status.HTTP_202_ACCEPTED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def sellerForget(request):
    try:
        data = request.data
        serializer = emailSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data["email"]
            if not SellerModel.objects.get(email=email):
                return Response({"message":"Account does not exists"}, status=status.HTTP_404_NOT_FOUND)
            thread_obj = send_forgot_link_seller(email)
            thread_obj.start()
            return Response({"message":"reset mail sent"}, status=status.HTTP_200_OK)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def sellerReset(request):
    try:
        data = request.data
        serializer = otpSerializer(data=data)
        if serializer.is_valid():
            otp = serializer.data["otp"]
            if not SellerOTP.objects.filter(otp=otp).first():
                return Response({"message":"OTP expired"}, status=status.HTTP_408_REQUEST_TIMEOUT)
            otp_obj = SellerOTP.objects.get(otp=otp)
            if otp_obj.is_valid == False:
                return Response({"message":"OTP expired"}, status=status.HTTP_408_REQUEST_TIMEOUT)
            if not SellerModel.objects.filter(email=otp_obj.user.email).first():
                return Response({"message":"user does not exist"}, status=status.HTTP_404_NOT_FOUND)
            user_obj = SellerModel.objects.get(email=otp_obj.user.email)
            npw = serializer.data["npw"]
            cpw = serializer.data["cpw"]
            if npw == cpw:
                user_obj.set_password(cpw)
                user_obj.save()
                return Response({"message":"Password changed successfull"}, status=status.HTTP_202_ACCEPTED)
        else:return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def sellerResendForgot(request):
    try:
        data = request.data
        serializer = emailSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data["email"]
            thread_obj = send_forgot_link_seller(email)
            thread_obj.start()
            return Response({"message":"OTP sent on your email"}, status=status.HTTP_200_OK)
        return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def sellerResendVerify(request):
    try:
        data = request.data
        serializer = emailSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data["email"]
            obj = SellerModel.objects.get(email=email)
            if obj.is_verified == True:
                return Response({"message":"Account already verified"}, status=status.HTTP_208_ALREADY_REPORTED)
            thread_obj = send_verification_email_seller(email)
            thread_obj.start()
            return Response({"message":"OTP sent on your email"}, status=status.HTTP_200_OK)
        return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
