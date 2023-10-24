from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

import simplejson as json

from accounts.views import check_role_customer
from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import User, UserProfile

from orders.models import Order, OrderedFood


# customer profile
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def c_profile(request):
    # get profile
    profile = get_object_or_404(UserProfile, user=request.user)

    # check request
    if request.method == 'POST':
        # get forms
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)

        # check data
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            # message
            messages.success(request, 'Profile updated successfully!')

            return redirect('customer')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        # get forms
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
    }

    return render(request, 'customers/c_profile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def my_orders(request):
    # get orders
    orders = Order.objects.filter(user=request.user).order_by('created_at')

    context = {
        'orders': orders,
    }

    return render(request, 'customers/my_orders.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def order_details(request, order_number):
    try:
        # get order and ordered food
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        # get total
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }

        return render(request, 'customers/order_details.html', context)
    except:
        return redirect('customer')
