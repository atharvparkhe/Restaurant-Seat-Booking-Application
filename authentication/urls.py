from django.urls import path
from . import views
from .views import *

urlpatterns = [
	path('signup/', views.signUp, name="signup"),
	path('verify/', views.verify, name="verify"),
	path('login/', views.logIn, name="login"),
	path('forgot/', views.forgot, name="forgot"),
	path('reset/', views.reset, name="reset"),
	path('resend/forgot/', views.resendForgot, name="resend-forgot"),
	path('resend/verify/', views.resendVerify, name="resend-verify"),

	path('seller-signup/', views.sellerSignUp, name="seller-signup"),
	path('seller-verify/', views.sellerVerify, name="seller-verify"),
    path('seller-login/', views.sellerLogIn, name="seller-login"),
	path('seller-forgot/', views.sellerForget, name="seller-forgot"),
	path('seller-reset/', views.sellerReset, name="seller-reset"),
    path('seller-resend-forgot/', views.sellerResendForgot, name="seller-resend-forgot"),
	path('seller-resend-verify/', views.sellerResendVerify, name="seller-resend-verify"),
]