from django.db import models
from base.models import *

class CustomerModel(BaseUser):
    def __str__(self):
        return self.email
    class Meta:
        db_table = 'customer'


class SellerModel(BaseUser):
    # aadhar_card = models.CharField(max_length=16, unique=True)
    gst_number = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'shopkeeper'


class OTPModel(BaseModel):
    otp = models.IntegerField()
    is_valid = models.BooleanField(default=False)
    user = models.ForeignKey(CustomerModel, related_name="customer_otp", on_delete=models.CASCADE)


class SellerOTP(BaseModel):
    otp = models.IntegerField()
    is_valid = models.BooleanField(default=False)
    user = models.ForeignKey(SellerModel, related_name="seller_otp", on_delete=models.CASCADE)