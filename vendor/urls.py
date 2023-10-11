from django.urls import path

from accounts import views as AccountViews

from . import views

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.v_profile, name='v_profile'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/',
         views.fooditems_by_category, name='fooditems_by_category'),

    # CRUD Category
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>/',
         views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/',
         views.delete_category, name='delete_category'),
]
