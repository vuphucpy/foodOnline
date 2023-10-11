from django.contrib import admin

from .models import Category, FoodItem


class CategoryAdmin(admin.ModelAdmin):
    # auto slug
    prepopulated_fields = {'slug': ('category_name',)}
    # display
    list_display = ('category_name', 'vendor', 'created_at')
    # search
    search_fields = ('category_name', 'vendor__vendor_name')


class FoodItemAdmin(admin.ModelAdmin):
    # auto slug
    prepopulated_fields = {'slug': ('food_title',)}
    # display
    list_display = ('food_title', 'category',
                    'vendor', 'price', 'is_available', 'updated_at',)
    # search
    search_fields = ('food_title', 'category__category_name',
                     'vendor__vendor_name', 'price',)
    # filter
    list_filter = ('is_available',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
