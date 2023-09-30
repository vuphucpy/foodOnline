from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from vendor.forms import VendorForm

from .forms import UserForm
from .models import User, UserProfile
from .utils import detectUser


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
        return redirect('dashboard')
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
            user = User.objects.create(
                first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            # add role
            user.role = User.CUSTOMER
            # save user
            user.save()

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
        return redirect('dashboard')
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
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = user_profile
            # save vendor
            vendor.save()

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
    return render(request, 'accounts/custDashboard.html')


# vendor dashboard
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')
