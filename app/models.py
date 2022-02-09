from django.db import models
from django.db.models.fields import related
from base.models import BaseModel
from authentication.models import CustomerModel, SellerModel

class RestaurantModel(BaseModel):
    owner = models.OneToOneField(SellerModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to="restaurant")
    address = models.TextField()
    town = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.IntegerField(null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    rating = models.IntegerField(default=0)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-created_at']

class RestaurantSeatsModel(BaseModel):
    restaurant = models.ForeignKey(RestaurantModel, related_name="restaurant_seats", on_delete=models.CASCADE)
    seat_name = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    def __str__(self):
        return self.seat_name

class OrderModel(BaseModel):
    owner = models.ForeignKey(CustomerModel, related_name="order_owner", on_delete=models.CASCADE)
    timing = models.DateTimeField(auto_now=False, auto_now_add=False)
    is_completed = models.BooleanField(default=False)
    def __str__(self):
        return self.owner.name

class OrderItemModel(BaseModel):
    order = models.ForeignKey(OrderModel, related_name="order_items", on_delete=models.CASCADE)
    owner = models.ForeignKey(CustomerModel, related_name="seat_owner", on_delete=models.CASCADE)
    seat = models.ForeignKey(RestaurantSeatsModel, related_name="booked_seat", on_delete=models.CASCADE)