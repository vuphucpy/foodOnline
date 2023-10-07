from django.shortcuts import render


# vendor profile
def v_profile(request):
    return render(request, 'vendor/v_profile.html')
