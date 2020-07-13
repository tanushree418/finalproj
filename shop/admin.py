from django.contrib import admin

# Register your models here.
from .models import Product, Contact, Orders, OrderUpdate

class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'user__username',
        'ref_code'
    ]
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Orders)
admin.site.register(OrderUpdate)