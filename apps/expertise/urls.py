from django.urls import path
from . import views

app_name = "expertise"

urlpatterns = [
    path("", views.specialty_list, name="list"),
    path("<slug:slug>/", views.specialty_detail, name="detail"),
]
