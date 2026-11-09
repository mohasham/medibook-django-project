from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import StyledAuthenticationForm

# Lets us write {% url 'accounts:login' %} in templates.
app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    # Django's built-in login view, using our styled form and our template.
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=StyledAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]