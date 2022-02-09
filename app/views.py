from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from authentication.models import SellerModel
from .models import *
from .threads import *
from .serializers import *


class RestaurantLC(ListCreateAPIView):
    queryset = RestaurantModel.objects.all()
    serializer_class = RestaurantGetSeriaizer
    def create(self, request, *args, **kwargs):
        try:
            authentication_classes = [JWTAuthentication]
            permission_classes = [IsAuthenticated]
            data = request.data
            seller_obj = SellerModel.objects.get(email=request.user.email)
            if RestaurantModel.objects.filter(owner=seller_obj):
                return Response({"message":"Restaurant already exists of this owner"}, status=status.HTTP_409_CONFLICT)
            serializer = RestaurantSerializer(data=data)
            if serializer.is_valid(self):
                serializer.save(owner=seller_obj)
                return Response({"message":"restaurant added", "data":serializer.data}, status=status.HTTP_202_ACCEPTED)
            return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RestaurantR(RetrieveAPIView):
    queryset = RestaurantModel.objects.all()
    serializer_class = RestaurantSerializer
    lookup_field = "id"

class RestaurantRUD(RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RestaurantModel.objects.all()
    serializer_class = RestaurantSerializer
    lookup_field = "id"


@api_view(["POST"])
def getSeats(request):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    try:
        data = request.data
        serializer = SeatingSerializer(data=data)
        if serializer.is_valid():
            if not RestaurantModel.objects.filter(id=serializer.data["restaurant_id"]).first():
                return Response({"message":"Invalid Restaurant ID"}, status=status.HTTP_404_NOT_FOUND)
            restaurant = RestaurantModel.objects.get(id=serializer.data["restaurant_id"])
            s1 = SeatSerializer(restaurant.restaurant_seats.all(), many=True)
            return Response({"data":s1.data}, status=status.HTTP_200_OK)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantSeatsRUD(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RestaurantSeatsModel.objects.all()
    serializer_class = SeatSerializer
    lookup_field = "id"


@api_view(["POST"])
def addSeats(request):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    try:
        data = request.data
        serializer = AddSeatSerializer(data=data)
        if serializer.is_valid():
            if not RestaurantModel.objects.filter(id=serializer.data["restaurant_id"]).first():
                return Response({"message":"Invalid Restaurant ID"}, status=status.HTTP_404_NOT_FOUND)
            RestaurantSeatsModel.objects.create(
                restaurant = RestaurantModel.objects.get(id=serializer.data["restaurant_id"]),
                seat_name = serializer.data["seat_name"]
            )
            return Response({"message":"Seat Added"}, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["POST"])
def seatBooking(request):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    try:
        data=request.data
        user = CustomerModel.objects.get(email = request.user.email)
        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            if not RestaurantModel.objects.filter(id=serializer.data["restaurant_id"]).first():
                return Response({"message":"Invalid Restaurant ID"}, status=status.HTTP_404_NOT_FOUND)
            restaurant = RestaurantModel.objects.get(id=serializer.data["restaurant_id"])
            seat_objs = RestaurantSeatsModel.objects.filter(restaurant=restaurant, is_available=True)
            if serializer.data["seats"] > seat_objs.count():
                return Response({"message":"Number of seats requested should not be greater than available seats"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            order_obj, _ = OrderModel.objects.get_or_create(owner=user, is_completed=False, timing = serializer.data["timing"])
            order_obj.save()
            for obj in seat_objs[:int(serializer.data["seats"])]:
                obj.is_available = False
                obj.user = user
                obj.save()
                OrderItemModel.objects.create(
                    seat = obj,
                    owner = user,
                    order = order_obj
                )
            s1 = OrderSerializer(order_obj)
            thread_obj1 = send_booking_mail(user.email, serializer.data["seats"], serializer.data["timing"], restaurant.name)
            thread_obj1.start()
            thread_obj2 = send_booking_mail_seller(restaurant.owner.email, serializer.data["seats"], serializer.data["timing"])
            thread_obj2.start()
            return Response({"message":"Seat(s) Booked", "data":s1.data}, status=status.HTTP_200_OK)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def sellerOrders(request):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    try:
        user = SellerModel.objects.get(email=request.user.email)
        if not OrderItemModel.objects.filter(seat__restaurant__owner=user):
            return Response({"message":"not enough data"}, status=status.HTTP_204_NO_CONTENT)
        objs = OrderItemModel.objects.filter(seat__restaurant__owner=user).order_by("-created_at")
        serializer = OrderItemsSerializer(objs, many=True)
        return Response({"data":serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def sellerComplete(request):
    try:
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated]
        data = request.data
        serializer = OrderUpdateSerializer(data=data)
        if serializer.is_valid():
            if not OrderModel.objects.filter(id=serializer.data["order_id"]):
                return Response({"data":serializer.data}, status=status.HTTP_404_NOT_FOUND)
            obj = OrderModel.objects.get(id=serializer.data["order_id"])
            if serializer.data["is_completed"] == True:
                obj.is_completed = True
                obj.save()
                for i in obj.order_items.all():
                    chair = RestaurantSeatsModel.objects.get(id=i.seat.id)
                    chair.is_available = True
                    chair.save()
                return Response({"message":"____ for seats has been removed"}, status=status.HTTP_200_OK)
        return Response({"data":serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def UserPastOrders(request):
    try:
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated]
        user = CustomerModel.objects.get(email = request.user.email)
        if not OrderModel.objects.filter(owner=user, is_completed=True):
            return Response({"message":"Insufficient Data"}, status=status.HTTP_206_PARTIAL_CONTENT)
        objs = OrderModel.objects.filter(owner=user, is_completed=True)
        serializer = UserOrderSerializer(objs, many=True)
        return Response({"data":serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error":str(e), "message":"Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
