from django.contrib import admin
from .models import *

class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_verified"]

admin.site.register(CustomerModel, CustomerModelAdmin)


class SellerModelAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_verified"]

admin.site.register(SellerModel, SellerModelAdmin)