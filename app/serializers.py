from rest_framework import serializers
from .models import *
from authentication.serializers import OwnerSerializer


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantSeatsModel
        exclude = ["created_at", "updated_at", "restaurant"]

class RestaurantGetSeriaizer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantModel
        fields = ["town", "state", "name", "logo", "id"]

class RestaurantSerializer(serializers.ModelSerializer):
    seats = serializers.SerializerMethodField()
    class Meta:
        model = RestaurantModel
        exclude = ["rating", "created_at", "updated_at", "owner"]
    def get_seats(self, obj):
        seats = 0
        try:
            restaurant = RestaurantModel.objects.get(id = obj.id)
            seats = restaurant.restaurant_seats.filter(is_available=True).count()
            return seats
        except Exception as e:
            print(e)


class SeatingSerializer(serializers.Serializer):
    restaurant_id = serializers.CharField(required=True)


class AddSeatSerializer(serializers.Serializer):
    restaurant_id = serializers.CharField(required=True)
    seat_name = serializers.CharField(required = True)


class BookingSerializer(serializers.Serializer):
    restaurant_id = serializers.CharField(required=True)
    seats = serializers.IntegerField(required = True)
    timing = serializers.DateTimeField(required = True)


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemModel
        exclude = ["owner"]


class OrderSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()
    class Meta:
        model = OrderModel
        exclude = ["owner", "updated_at"]
    def get_cart_items(self, obj):
        cart_items = []
        try:
            cart_obj = OrderModel.objects.get(id = obj.id)
            serializer = OrderItemsSerializer(cart_obj.order_items.all(), many=True)
            cart_items = serializer.data
            return cart_items
        except Exception as e:
            print(e)

class OrderUpdateSerializer(serializers.Serializer):
    order_id = serializers.CharField(required = True)
    is_completed = serializers.BooleanField(required = True)


class UserOrderSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()
    class Meta:
        model = OrderModel
        exclude = ["owner", "updated_at", "id", "is_completed"]
    def get_cart_items(self, obj):
        cart_items = 0
        try:
            cart_items = obj.order_items.all().count()
            return int(cart_items)
        except Exception as e:
            print(e)