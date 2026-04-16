from django.urls import path
from . import views

app_name = "doctor_admin"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]
