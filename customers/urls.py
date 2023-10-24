from django.urls import path

from accounts import views as AccountViews

from . import views


urlpatterns = [
    path('', AccountViews.custDashboard, name='customer'),
    path('profile/', views.c_profile, name='c_profile'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-details/<int:order_number>',
         views.order_details, name='order_details'),
]
