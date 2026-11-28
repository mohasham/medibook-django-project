from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import PatientRegistrationForm


def register(request):
    # Already logged in? No need to register again.
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log them in straight after registering
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("home")
    else:
        form = PatientRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required  # anonymous visitors are sent to LOGIN_URL
def home(request):
    """Landing page after login. Real dashboards come in 7b and 7c;
    for now this shows a simple placeholder."""
    return render(request, "home.html")