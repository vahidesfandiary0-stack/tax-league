from django.shortcuts import render


def home(request):
    """Public marketing homepage for the RAQTIVA tax league."""
    return render(request, "landing/home.html")
