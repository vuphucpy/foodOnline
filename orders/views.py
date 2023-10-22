from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

import simplejson as json

from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts

from accounts.utils import send_notification

from .forms import OrderForm
from .models import Order, Payment, OrderedFood
from .utils import generate_order_number


@login_required(login_url='login')
def place_order(request):
    # get cart items
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    # cart count
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('marketplace')

    # get cart amount
    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']

    # check request
    if request.method == "POST":
        form = OrderForm(request.POST)

        # check data
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()

            context = {
                'order': order,
                'cart_items': cart_items,
            }

            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)

    return render(request, 'orders/place_order.html')


@login_required(login_url='login')
def payments(request):
    # check request ajax
    if request.headers.get('x-requested-with') == "XMLHttpRequest" and request.method == "POST":
        # store the payment detail in the payment models
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        # get order
        order = Order.objects.get(user=request.user, order_number=order_number)
        # instance payment
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status
        )
        payment.save()

        # update the order model
        order.payment = payment
        order.is_ordered = True
        order.save()

        # move the cart items to order food model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.food_item = item.food_item
            ordered_food.quantity = item.quantity
            ordered_food.price = item.food_item.price
            ordered_food.amount = item.food_item.price * item.quantity
            ordered_food.save()

        # send order confirm email
        mail_subject = 'Thank you for ordering with us'
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
        }
        send_notification(mail_subject, mail_template, context)

        # send order received email to the vendor
        mail_subject = 'You have received a new order'
        mail_template = 'orders/new_order_received.html'
        to_emails = []

        # get vendor email
        for i in cart_items:
            if i.food_item.vendor.user.email not in to_emails:
                to_emails.append(i.food_item.vendor.user.email)

        context = {
            'user': request.user,
            'order': order,
            'to_email': to_emails,
        }
        send_notification(mail_subject, mail_template, context)

        # clear the cart if payment success
        # cart_items.delete()

        # return back to ajax with status success or failure
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)
    return HttpResponse('payment view')


@login_required(login_url='login')
def order_complete(request):
    # get data
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        # get order
        order = Order.objects.get(
            order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        # get order food
        ordered_food = OrderedFood.objects.filter(order=order)

        # subtotal
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

        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')
