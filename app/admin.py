from django.contrib import admin
from .models import *

class RestaurantSeatsModelAdmin(admin.StackedInline):
    model = RestaurantSeatsModel
    fk_name = 'restaurant'

@admin.register(RestaurantModel)
class RestaurantModelAdmin(admin.ModelAdmin):
    inlines = [ RestaurantSeatsModelAdmin ]

admin.site.register(OrderModel)
admin.site.register(OrderItemModel)