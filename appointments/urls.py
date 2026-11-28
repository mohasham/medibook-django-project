from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("book/<int:doctor_id>/", views.book, name="book"),
    path("mine/", views.my_appointments, name="mine"),
    path("<int:pk>/cancel/", views.cancel, name="cancel"),
    path("<int:pk>/reschedule/", views.reschedule, name="reschedule"),
]