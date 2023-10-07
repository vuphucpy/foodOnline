from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor

from .forms import VendorForm
from .models import Vendor


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
