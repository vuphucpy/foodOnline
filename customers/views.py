from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from accounts.views import check_role_customer
from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import User, UserProfile


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
