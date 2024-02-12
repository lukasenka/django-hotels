from django.contrib import admin
from .models import Balance, Hotel, Order, AdminDetails, Profile

admin.site.register(Balance)
admin.site.register(Hotel)
admin.site.register(Order)
admin.site.register(AdminDetails)
admin.site.register(Profile)
