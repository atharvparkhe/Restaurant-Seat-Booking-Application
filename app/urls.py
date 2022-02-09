from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('restaurants/', views.RestaurantLC.as_view(), name="RestaurantL"),
    path('restaurant/<id>/', views.RestaurantR.as_view(), name="RestaurantR"),
    path('seller-restaurant/<id>/', views.RestaurantRUD.as_view(), name="RestaurantRUD"),
    path('get-seats/', views.getSeats, name="getSeats"),
    path('add-seat/', views.addSeats, name="addSeats"),
    path('seat/<id>/', views.RestaurantSeatsRUD.as_view(), name="RestaurantSeatsRUD"),
    path('booking/', views.seatBooking, name="seatBooking"),
    path('seller-update-orders/', views.sellerComplete, name="sellerComplete"),
    path('previous-bookings/', views.sellerOrders, name="sellerOrders"),
    path('past-bookings/', views.UserPastOrders, name="UserPreviousOrders"),
]