from django.shortcuts import render, redirect
from django.contrib import messages

from vendor.forms import VendorForm

from .forms import UserForm
from .models import User, UserProfile

# register user function


def registerUser(request):
    # check post method
    if request.method == 'POST':
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

            return redirect('registerUser')
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
    # check post method
    if request.method == 'POST':
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
            user = User.objects.create(
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

            return redirect('registerVendor')
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
