"""Public-facing core views."""
from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from apps.blog.models import BlogPost
from apps.expertise.models import SpecialtyArea
from apps.media_library.models import Video
from apps.publications.models import Publication

from .forms import ContactForm
from .models import DoctorProfile


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or None


def home(request):
    doctor = DoctorProfile.load()
    featured_specialties = (
        SpecialtyArea.objects.filter(is_featured=True).order_by("order")[:6]
    )
    featured_videos = (
        Video.objects.filter(is_featured=True).order_by("-is_official_acibadem", "order")[:4]
    )
    # Hero on the home page is always the Acıbadem Instagram Reel — YouTube
    # videos show only in the "Videolar" section below, never in the hero slot.
    hero_video = (
        Video.objects.filter(platform="instagram", is_official_acibadem=True)
        .order_by("-is_featured", "order").first()
        or Video.objects.filter(platform="instagram")
        .order_by("-is_featured", "-publish_date").first()
    )
    featured_publications = (
        Publication.objects.filter(is_featured=True).order_by("-year")[:3]
    )
    recent_posts = BlogPost.objects.filter(status="published").order_by("-published_at")[:3]

    return render(request, "core/home.html", {
        "doctor": doctor,
        "featured_specialties": featured_specialties,
        "featured_videos": featured_videos,
        "hero_video": hero_video,
        "featured_publications": featured_publications,
        "recent_posts": recent_posts,
    })


def about(request):
    from apps.experience.models import Education, Experience, Membership

    return render(request, "core/about.html", {
        "doctor": DoctorProfile.load(),
        "educations": Education.objects.all(),
        "experiences": Experience.objects.all(),
        "memberships": Membership.objects.all(),
    })


@require_http_methods(["GET", "POST"])
def contact(request):
    doctor = DoctorProfile.load()
    success = False
    form = ContactForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ip_address = _client_ip(request)
            obj.save()
            success = True

            # Notify the admin — best-effort; don't block the form if it fails.
            try:
                notify_to = getattr(settings, "CONTACT_NOTIFICATION_EMAIL", "")
                if notify_to:
                    send_mail(
                        subject=f"[drsavasgundogan] Yeni mesaj: {obj.name}",
                        message=(
                            f"Ad: {obj.name}\n"
                            f"E-posta: {obj.email}\n"
                            f"Telefon: {obj.phone}\n"
                            f"Konu: {obj.subject}\n\n"
                            f"{obj.message}"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[notify_to],
                        fail_silently=True,
                    )
            except Exception:
                pass

            form = ContactForm()

    if request.headers.get("HX-Request"):
        return render(request, "core/_contact_form_partial.html", {
            "form": form, "success": success,
        })

    return render(request, "core/contact.html", {
        "doctor": doctor, "form": form, "success": success,
    })


def privacy(request):
    return render(request, "core/privacy.html", {
        "doctor": DoctorProfile.load(),
        "body_field": "privacy_body",
        "page_title": _("Gizlilik Politikası"),
    })


def kvkk(request):
    return render(request, "core/privacy.html", {
        "doctor": DoctorProfile.load(),
        "body_field": "kvkk_body",
        "page_title": _("Aydınlatma Metni"),
    })


def custom_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def custom_500(request):
    return render(request, "errors/500.html", status=500)
