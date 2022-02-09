import threading, random
from django.conf import settings
from django.core.mail import send_mail
from .models import *


class send_verification_email(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        try:
            otp = random.randint(100001, 999999)
            OTPModel.objects.create(otp=otp,is_valid=True ,user=CustomerModel.objects.get(email=self.email))
            subject = "Link to verify the your Account"
            message = f"The OTP to verify your email is {otp} \nIts valid only for 5 mins."
            email_from = settings.EMAIL_HOST_USER
            print("Email send started")
            send_mail(subject , message ,email_from ,[self.email])
            print("Email send finished")
        except Exception as e:
            print(e)

class send_forgot_link(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        try:
            otp = random.randint(100001, 999999)
            OTPModel.objects.create(otp=otp,is_valid=True ,user=CustomerModel.objects.get(email=self.email))
            subject = "OTP to change password"
            message = f"The OTP to change your account password {otp} \nIts valid only for 5 mins."
            email_from = settings.EMAIL_HOST_USER
            print("Email send started")
            send_mail(subject , message ,email_from ,[self.email])
            print("Email send finished")
        except Exception as e:
                print(e)

class send_verification_email_seller(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        try:
            otp = random.randint(100001, 999999)
            SellerOTP.objects.create(otp=otp,is_valid=True ,user=SellerModel.objects.get(email=self.email))
            subject = "Link to verify the your Account"
            message = f"The OTP to verify your email is {otp} \nIts valid only for 5 mins."
            email_from = settings.EMAIL_HOST_USER
            print("Email send started")
            send_mail(subject , message ,email_from ,[self.email])
            print("Email send finished")
        except Exception as e:
            print(e)

class send_forgot_link_seller(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        try:
            otp = random.randint(100001, 999999)
            SellerOTP.objects.create(otp=otp,is_valid=True ,user=SellerModel.objects.get(email=self.email))
            subject = "OTP to change password"
            message = f"The OTP to change your account password {otp} \nIts valid only for 5 mins."
            email_from = settings.EMAIL_HOST_USER
            print("Email send started")
            send_mail(subject , message ,email_from ,[self.email])
            print("Email send finished")
        except Exception as e:
                print(e)