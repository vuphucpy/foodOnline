from django.shortcuts import render
from vendor.models import Vendor


# home page
def home(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)

    context = {
        'vendors': vendors,
    }

    return render(request, "home.html", context)
