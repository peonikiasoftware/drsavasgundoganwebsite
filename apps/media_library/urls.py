from django.urls import path
from . import views

app_name = "media_library"

urlpatterns = [
    path("", views.video_list, name="list"),
]
