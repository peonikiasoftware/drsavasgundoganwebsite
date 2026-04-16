from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("hakkimda/", views.about, name="about"),
    path("iletisim/", views.contact, name="contact"),
    path("gizlilik/", views.privacy, name="privacy"),
    path("aydinlatma-metni/", views.kvkk, name="kvkk"),
]
