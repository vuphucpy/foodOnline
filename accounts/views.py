from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import UserForm
from .models import User


def registerUser(request):
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
            user.role = User.CUSTOMER
            user.save()

            # message
            messages.success(
                request, 'Your account has been registered successfully!')

            return redirect('registerUser')
        else:
            messages.error(request, 'Your account has been registered fail')
            print('Invalid form')
            print(form.errors)
    else:
        form = UserForm()

    context = {
        'form': form,
    }

    return render(request, 'accounts/registerUser.html', context)
