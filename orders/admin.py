from django.contrib import admin

from .models import Payment, Order, OrderedFood


class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('order', 'payment', 'user',
                       'food_item', 'quantity', 'price', 'amount')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'name', 'phone', 'email',
                    'total', 'payment_method', 'status', 'order_place_to', 'is_ordered')
    inlines = [OrderedFoodInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)
