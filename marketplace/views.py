from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from datetime import date, datetime

from vendor.models import Vendor, OpeningHour

from accounts.models import UserProfile

from menu.models import Category, FoodItem

from orders.forms import OrderForm

from .models import Cart
from .context_processors import get_cart_counter, get_cart_amounts


# marketplace
def marketplace(request):
    # get vendor
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)

    context = {
        'vendors': vendors,
    }

    return render(request, 'marketplace/listings.html', context)


# vendor detail
def vendor_detail(request, vendor_slug):
    # get vendor
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    # get categories
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True),
        )
    )

    # get opening hours
    opening_hours = OpeningHour.objects.filter(
        vendor=vendor).order_by('day', '-from_hour')

    # check current day's opening hours
    today_date = date.today()
    today = today_date.isoweekday()
    current_opening_hours = OpeningHour.objects.filter(
        vendor=vendor, day=today)

    # check user
    if request.user.is_authenticated:
        # get cart items
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
    }

    return render(request, 'marketplace/vendor_detail.html', context)


# add to cart
def add_to_cart(request, food_id):
    # check user login
    if request.user.is_authenticated:
        # check ajax
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if the food item exists
            try:
                # get food item
                food_item = FoodItem.objects.get(id=food_id)

                # check if the user has already added that food to the cart
                try:
                    check_cart = Cart.objects.get(
                        user=request.user, food_item=food_item)

                    # Increase the cart quantity
                    check_cart.quantity += 1
                    check_cart.save()

                    return JsonResponse({
                        'status': 'Success',
                        'message': 'Increase the cart quantity',
                        'cart_counter': get_cart_counter(request),
                        'qty': check_cart.quantity,
                        'cart_amounts': get_cart_amounts(request),
                    })
                except:
                    # create cart if that food does not exist
                    check_cart = Cart.objects.create(
                        user=request.user, food_item=food_item, quantity=1)

                    return JsonResponse({
                        'status': 'Success',
                        'message': 'Added the food to the cart',
                        'cart_counter': get_cart_counter(request),
                        'qty': check_cart.quantity,
                        'cart_amounts': get_cart_amounts(request),
                    })
            except:
                return JsonResponse({
                    'status': 'Success',
                    'message': 'This food does not exist!',
                })
        else:
            return JsonResponse({
                'status': 'Failed',
                'message': 'Invalid request',
            })
    else:
        return JsonResponse({
            'status': 'Login_required',
            'message': 'Please login to continue',
        })


# decrease cart
def decrease_cart(request, food_id):
    # check user login
    if request.user.is_authenticated:
        # check ajax
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if the food item exists
            try:
                # get food item
                food_item = FoodItem.objects.get(id=food_id)

                # check if the user has already added that food to the cart
                try:
                    check_cart = Cart.objects.get(
                        user=request.user, food_item=food_item)

                    if check_cart.quantity > 1:
                        # Decrease the cart quantity
                        check_cart.quantity -= 1
                        check_cart.save()
                    else:
                        check_cart.delete()
                        check_cart.quantity = 0

                    return JsonResponse({
                        'status': 'Success',
                        'message': 'Decrease the cart quantity',
                        'cart_counter': get_cart_counter(request),
                        'qty': check_cart.quantity,
                        'cart_amounts': get_cart_amounts(request)
                    })
                except:
                    return JsonResponse({
                        'status': 'Failed',
                        'message': 'You do not have this item in the cart',
                    })
            except:
                return JsonResponse({
                    'status': 'Success',
                    'message': 'This food does not exist!',
                })
        else:
            return JsonResponse({
                'status': 'Failed',
                'message': 'Invalid request',
            })
    else:
        return JsonResponse({
            'status': 'Login_required',
            'message': 'Please login to continue',
        })


# cart
@login_required(login_url='login')
def cart(request):
    # get cart items
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')

    context = {
        'cart_items': cart_items,
    }

    return render(request, 'marketplace/cart.html', context)


# delete cart
def delete_cart(request, cart_id):
    # check user
    if request.user.is_authenticated:
        # check ajax
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # check the cart item exist
                cart_item = Cart.objects.get(user=request.user, id=cart_id)

                if cart_item:
                    cart_item.delete()
                    return JsonResponse({
                        'status': 'Success',
                        'message': 'Cart item has been delete!',
                        'cart_counter': get_cart_counter(request),
                        'cart_amounts': get_cart_amounts(request)
                    })
            except:
                return JsonResponse({
                    'status': 'Failed',
                    'message': 'Cart item does not exist',
                })
        else:
            return JsonResponse({
                'status': 'Failed',
                'message': 'Invalid request',
            })


# search
def search(request):
    keyword = request.GET['restaurant_name']

    # get vendor ids that has the food item the user is looking for
    fetch_vendor_by_food_items = FoodItem.objects.filter(
        food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)

    # get vendor
    vendors = Vendor.objects.filter(Q(id__in=fetch_vendor_by_food_items) | Q(
        vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
    # vendor count
    vendor_count = vendors.count()

    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }

    return render(request, 'marketplace/listings.html', context)


@login_required(login_url='login')
def checkout(request):
    # get cart items
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    # cart count
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('marketplace')

    # get user profile
    user_profile = UserProfile.objects.get(user=request.user)

    # default values
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }

    # get form
    form = OrderForm(initial=default_values)

    context = {
        'form': form,
        'cart_items': cart_items,
    }

    return render(request, 'marketplace/checkout.html', context)
