from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.template.defaultfilters import slugify

import datetime

from vendor.forms import VendorForm
from vendor.models import Vendor

from orders.models import Order

from .forms import UserForm
from .models import User, UserProfile
from .utils import detectUser, send_verification_email


# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    # if user logged in
    if request.user.is_authenticated:
        # messages
        messages.warning(request, 'You are already logged in.')
        return redirect('myAccount')
    # check post method
    elif request.method == 'POST':
        # get data
        form = UserForm(request.POST)

        # check data
        if form.is_valid():
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Get data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # create instance
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            # add role
            user.role = User.CUSTOMER
            # save user
            user.save()

            # Send verification email
            mail_subject = 'Please active your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(
                request, user, mail_subject, email_template)

            # message
            messages.success(
                request, 'Your account has been registered successfully!')

            return redirect('login')
        else:
            # message
            messages.error(request, 'Your account has been registered failed')
            print('Invalid form')
            print(form.errors)
    else:
        # get form
        form = UserForm()

    # send data to client
    context = {
        'form': form,
    }

    return render(request, 'accounts/registerUser.html', context)


# register vendor function
def registerVendor(request):
    # if user logged in
    if request.user.is_authenticated:
        # messages
        messages.warning(request, 'You are already logged in.')
        return redirect('myAccount')
    # check post method
    elif request.method == 'POST':
        # store the data and create user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        # check data
        if form.is_valid() and v_form.is_valid():
            # Get data user
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # create instance
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            # add role
            user.role = User.VENDOR
            # save user
            user.save()

            # get user profile
            user_profile = UserProfile.objects.get(user=user)

            # get vendor data form
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = user_profile
            vendor.vendor_slug = slugify(vendor_name)
            # save vendor
            vendor.save()

            # Send verification email
            mail_subject = 'Please active your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(
                request, user, mail_subject, email_template)

            # message
            messages.success(
                request, 'Your account has been registered successfully!')

            return redirect('login')
        else:
            # message
            messages.error(request, 'Your account has been registered failed')
            print('Invalid form')
            print(form.errors)
            print(v_form.errors)
    else:
        # get forms
        form = UserForm()
        v_form = VendorForm()

    # send data to client
    context = {
        'form': form,
        'v_form': v_form,
    }

    return render(request, 'accounts/registerVendor.html', context)


# activate function
def activate(request, uidb64, token):
    # Activate the user by setting the is_active status is True
    try:
        # decode
        uid = urlsafe_base64_decode(uidb64).decode()
        # get user
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # check user and token
    if user is not None and default_token_generator.check_token(user, token):
        # active True
        user.is_active = True
        user.save()
        # message
        messages.success(request, 'Congratulation! Your account is activated.')

        return redirect('myAccount')
    else:
        # message
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')


# logged in
def login(request):
    # if user logged in
    if request.user.is_authenticated:
        # messages
        messages.warning(request, 'You are already logged in.')
        return redirect('myAccount')
    # check post method
    elif request.method == 'POST':
        # get data
        email = request.POST['email']
        password = request.POST['password']

        # get user
        user = auth.authenticate(email=email, password=password)

        # check user
        if user is not None:
            # login user
            auth.login(request, user)
            # message
            messages.success(request, 'You are now logged in')

            return redirect('myAccount')
        else:
            # messages
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')


# logged out
@login_required(login_url='login')
def logout(request):
    # logout user
    auth.logout(request)
    # message
    messages.info(request, 'You are logged out.')
    return redirect('login')


# detect user
@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


# customer dashboard
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    # get order limit 5
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders[:5]

    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
    }

    return render(request, 'accounts/custDashboard.html', context)


# vendor dashboard
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    # get vendor
    vendor = Vendor.objects.get(user=request.user)
    # get orders
    orders = Order.objects.filter(
        vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]

    # current month's revenue
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(
        vendors__in=[vendor.id], created_at__month=current_month)

    # total month
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']

    # total revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()['grand_total']

    context = {
        'vendor': vendor,
        'order_count': orders.count(),
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
    }

    return render(request, 'accounts/vendorDashboard.html', context)


# forgot password
def forgot_password(request):
    # check post method
    if request.method == 'POST':
        # get email
        email = request.POST['email']

        # if email exist
        if User.objects.filter(email=email).exists():
            # get user
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset your password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(
                request, user, mail_subject, email_template)

            # message
            messages.success(
                request, 'Password reset link has been send to your email address.')

            return redirect('login')
        else:
            # message
            messages.error(request, 'Account does not exist.')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')


# reset_password_validate
def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    # Activate the user by setting the is_active status is True
    try:
        # decode
        uid = urlsafe_base64_decode(uidb64).decode()
        # get user
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # check user and token
    if user is not None and default_token_generator.check_token(user, token):
        # create session and save data
        request.session['uid'] = uid
        # message
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        # message
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')


# reset_password
def reset_password(request):
    # check post method
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # compare password and confirm password
        if password == confirm_password:
            # get uid -> session
            uid = request.session.get('uid')
            # get user
            user = User.objects.get(pk=uid)
            # set password
            user.set_password(password)
            # set active
            user.is_active = True
            user.save()

            # message
            messages.success(request, 'Password reset successful.')

            return redirect('login')
        else:
            messages.error(request, 'Password does not match.')
            return redirect('reset_password')

    return render(request, 'accounts/reset_password.html')
