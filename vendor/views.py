from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor

from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm

from .forms import VendorForm
from .models import Vendor


# get vendor
def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


# vendor profile
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def v_profile(request):
    # get data
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    # check request
    if request.method == 'POST':
        # get data
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        # check data
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()

            # message
            messages.success(request, 'Settings Updated.')

            return redirect('v_profile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        # get forms
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }

    return render(request, 'vendor/v_profile.html', context)


# menu builder
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    # get data
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')

    context = {
        'categories': categories,
    }

    return render(request, 'vendor/menu_builder.html', context)


# food items by category
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    # get data
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)

    # get food items
    foodItems = FoodItem.objects.filter(
        vendor=vendor, category=category).order_by('created_at')

    context = {
        'fooditems': foodItems,
        'category': category,
    }

    return render(request, 'vendor/fooditems_by_category.html', context)


# add category
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    # check request
    if request.method == 'POST':
        # get data
        form = CategoryForm(request.POST)

    # check data and save category
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category.save()
            # message
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        # get form
        form = CategoryForm()

    context = {
        'form': form,
    }

    return render(request, 'vendor/add_category.html', context)


# edit category
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    # get category
    category = get_object_or_404(Category, pk=pk)

    # check request
    if request.method == 'POST':
        # get data
        form = CategoryForm(request.POST, instance=category)

    # check data and save category
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category.save()
            # message
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        # get form
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
    }

    return render(request, 'vendor/edit_category.html', context)


# delete category
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('menu_builder')


# add food item
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    # check request
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)

        # check data
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            food.save()
            # message
            messages.success(request, 'Food item added successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # modify this form
        form.fields['category'].queryset = Category.objects.filter(
            vendor=get_vendor(request))

    context = {
        'form': form,
    }

    return render(request, 'vendor/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    # get food
    food = get_object_or_404(FoodItem, pk=pk)

    # check request
    if request.method == 'POST':
        # get data
        form = FoodItemForm(request.POST, request.FILES, instance=food)

    # check data and save category
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            food.save()
            # message
            messages.success(request, 'Food item updated successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        # get form
        form = FoodItemForm(instance=food)
        # modify this form
        form.fields['category'].queryset = Category.objects.filter(
            vendor=get_vendor(request))

    context = {
        'form': form,
        'food': food,
    }

    return render(request, 'vendor/edit_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food item deleted successfully!')
    return redirect('fooditems_by_category', food.category.id)
