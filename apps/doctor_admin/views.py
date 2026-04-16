"""Doctor-friendly admin dashboard (/doctor-admin/)."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator

from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.blog.models import BlogPost
from apps.core.models import ContactMessage, DoctorProfile, PageView
from apps.experience.models import Education, Experience, Membership
from apps.expertise.models import SpecialtyArea
from apps.faq.models import FAQItem
from apps.media_library.models import Video
from apps.publications.models import Publication

from .decorators import doctor_required
from .forms import (
    BlogPostForm,
    DoctorProfileForm,
    EducationForm,
    ExperienceForm,
    FAQItemForm,
    MembershipForm,
    PublicationForm,
    SpecialtyAreaForm,
    VideoForm,
)


# ------------------------------------------------------------------
# Auth views
# ------------------------------------------------------------------
class DoctorLoginView(LoginView):
    template_name = "doctor_admin/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse("doctor_admin:dashboard")


class DoctorLogoutView(LogoutView):
    next_page = "/doctor-admin/login/"


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------
@doctor_required
def dashboard(request):
    unread_messages = ContactMessage.objects.filter(is_read=False, is_archived=False).count()
    recent_messages = ContactMessage.objects.order_by("-created_at")[:5]
    stats = {
        "publications": Publication.objects.count(),
        "specialties": SpecialtyArea.objects.count(),
        "videos": Video.objects.count(),
        "blog_posts": BlogPost.objects.count(),
        "education": Education.objects.count(),
        "experience": Experience.objects.count(),
        "faq": FAQItem.objects.count(),
        "memberships": Membership.objects.count(),
    }

    # Headline analytics teasers
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    last_7 = now - timedelta(days=7)
    human = PageView.objects.filter(is_bot=False)
    analytics_summary = {
        "today": human.filter(created_at__gte=today).count(),
        "last_7d": human.filter(created_at__gte=last_7).count(),
        "unique_7d": human.filter(created_at__gte=last_7).values("visitor_hash").distinct().count(),
    }

    return render(request, "doctor_admin/dashboard.html", {
        "unread_messages": unread_messages,
        "recent_messages": recent_messages,
        "stats": stats,
        "analytics_summary": analytics_summary,
        "doctor": DoctorProfile.load(),
    })


@doctor_required
def analytics(request):
    """30-day traffic dashboard."""
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    last_7 = now - timedelta(days=7)
    last_30 = now - timedelta(days=30)

    try:
        period_days = max(1, min(90, int(request.GET.get("days") or 30)))
    except (TypeError, ValueError):
        period_days = 30
    period_start = now - timedelta(days=period_days)

    human = PageView.objects.filter(is_bot=False)
    period = human.filter(created_at__gte=period_start)

    # Top-line counters
    totals = {
        "today":       human.filter(created_at__gte=today).count(),
        "yesterday":   human.filter(
            created_at__gte=today - timedelta(days=1),
            created_at__lt=today,
        ).count(),
        "last_7d":     human.filter(created_at__gte=last_7).count(),
        "last_30d":    human.filter(created_at__gte=last_30).count(),
        "unique_7d":   human.filter(created_at__gte=last_7).values("visitor_hash").distinct().count(),
        "unique_30d":  human.filter(created_at__gte=last_30).values("visitor_hash").distinct().count(),
        "bots_30d":    PageView.objects.filter(is_bot=True, created_at__gte=last_30).count(),
        "total_ever":  PageView.objects.filter(is_bot=False).count(),
    }

    # Top pages
    top_pages = list(
        period.values("path")
              .annotate(views=Count("id"))
              .order_by("-views")[:12]
    )

    # Language split
    lang = list(
        period.values("language")
              .annotate(views=Count("id"))
              .order_by("-views")
    )
    # Device split
    device = list(
        period.values("device_type")
              .annotate(views=Count("id"))
              .order_by("-views")
    )
    # Top countries (Vercel adds x-vercel-ip-country header)
    countries = list(
        period.exclude(country="")
              .values("country")
              .annotate(views=Count("id"))
              .order_by("-views")[:8]
    )
    # Top referrers (strip own domain)
    referrers = list(
        period.exclude(referrer="")
              .values("referrer")
              .annotate(views=Count("id"))
              .order_by("-views")[:8]
    )

    # Daily trend (for the sparkline chart)
    daily_rows = list(
        period.annotate(day=TruncDate("created_at"))
              .values("day")
              .annotate(views=Count("id"))
              .order_by("day")
    )
    day_map = {r["day"]: r["views"] for r in daily_rows}
    daily = []
    for i in range(period_days):
        d = (now - timedelta(days=period_days - 1 - i)).date()
        daily.append({"day": d, "views": day_map.get(d, 0)})
    max_day = max((d["views"] for d in daily), default=1) or 1

    return render(request, "doctor_admin/analytics.html", {
        "totals": totals,
        "top_pages": top_pages,
        "lang": lang,
        "device": device,
        "countries": countries,
        "referrers": referrers,
        "daily": daily,
        "max_day": max_day,
        "period_days": period_days,
    })


# ------------------------------------------------------------------
# Doctor profile (single-object edit)
# ------------------------------------------------------------------
@doctor_required
def profile_edit(request):
    instance = DoctorProfile.load()
    form = DoctorProfileForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profil güncellendi.")
        return redirect("doctor_admin:profile")
    return render(request, "doctor_admin/profile_edit.html", {"form": form})


# ------------------------------------------------------------------
# Generic list/add/edit/delete factory
# ------------------------------------------------------------------
def _generic_list(model, template, title, add_url_name, edit_url_name, delete_url_name):
    @doctor_required
    def _view(request):
        objects = model.objects.all()
        return render(request, template, {
            "objects": objects,
            "title": title,
            "add_url_name": add_url_name,
            "edit_url_name": edit_url_name,
            "delete_url_name": delete_url_name,
        })
    return _view


def _generic_edit(model, form_cls, redirect_name, title):
    @doctor_required
    def _view(request, pk=None):
        instance = get_object_or_404(model, pk=pk) if pk else None
        form = form_cls(
            request.POST or None,
            request.FILES or None,
            instance=instance,
        )
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, "Kaydedildi.")
            return redirect(redirect_name)
        return render(request, "doctor_admin/form.html", {
            "form": form, "title": title,
            "object": instance,
            "redirect_name": redirect_name,
        })
    return _view


def _generic_delete(model, redirect_name):
    @doctor_required
    def _view(request, pk):
        obj = get_object_or_404(model, pk=pk)
        if request.method == "POST":
            obj.delete()
            messages.success(request, "Silindi.")
            return redirect(redirect_name)
        return render(request, "doctor_admin/confirm_delete.html", {
            "object": obj, "redirect_name": redirect_name,
        })
    return _view


# ------------------------------------------------------------------
# Education
# ------------------------------------------------------------------
education_list = _generic_list(
    Education, "doctor_admin/list.html", "Eğitim",
    "doctor_admin:education_add",
    "doctor_admin:education_edit",
    "doctor_admin:education_delete",
)
education_add = _generic_edit(
    Education, EducationForm, "doctor_admin:education_list", "Yeni Eğitim",
)
education_edit = _generic_edit(
    Education, EducationForm, "doctor_admin:education_list", "Eğitim Düzenle",
)
education_delete = _generic_delete(Education, "doctor_admin:education_list")


# ------------------------------------------------------------------
# Experience
# ------------------------------------------------------------------
experience_list = _generic_list(
    Experience, "doctor_admin/list.html", "Deneyim",
    "doctor_admin:experience_add",
    "doctor_admin:experience_edit",
    "doctor_admin:experience_delete",
)
experience_add = _generic_edit(
    Experience, ExperienceForm, "doctor_admin:experience_list", "Yeni Deneyim",
)
experience_edit = _generic_edit(
    Experience, ExperienceForm, "doctor_admin:experience_list", "Deneyim Düzenle",
)
experience_delete = _generic_delete(Experience, "doctor_admin:experience_list")


# ------------------------------------------------------------------
# Membership
# ------------------------------------------------------------------
membership_list = _generic_list(
    Membership, "doctor_admin/list.html", "Üyelikler",
    "doctor_admin:membership_add",
    "doctor_admin:membership_edit",
    "doctor_admin:membership_delete",
)
membership_add = _generic_edit(
    Membership, MembershipForm, "doctor_admin:membership_list", "Yeni Üyelik",
)
membership_edit = _generic_edit(
    Membership, MembershipForm, "doctor_admin:membership_list", "Üyelik Düzenle",
)
membership_delete = _generic_delete(Membership, "doctor_admin:membership_list")


# ------------------------------------------------------------------
# Publications
# ------------------------------------------------------------------
publication_list = _generic_list(
    Publication, "doctor_admin/list.html", "Yayınlar",
    "doctor_admin:publication_add",
    "doctor_admin:publication_edit",
    "doctor_admin:publication_delete",
)
publication_add = _generic_edit(
    Publication, PublicationForm, "doctor_admin:publication_list", "Yeni Yayın",
)
publication_edit = _generic_edit(
    Publication, PublicationForm, "doctor_admin:publication_list", "Yayın Düzenle",
)
publication_delete = _generic_delete(Publication, "doctor_admin:publication_list")


# ------------------------------------------------------------------
# Videos
# ------------------------------------------------------------------
video_list = _generic_list(
    Video, "doctor_admin/list.html", "Videolar",
    "doctor_admin:video_add",
    "doctor_admin:video_edit",
    "doctor_admin:video_delete",
)
video_add = _generic_edit(
    Video, VideoForm, "doctor_admin:video_list", "Yeni Video",
)
video_edit = _generic_edit(
    Video, VideoForm, "doctor_admin:video_list", "Video Düzenle",
)
video_delete = _generic_delete(Video, "doctor_admin:video_list")


# ------------------------------------------------------------------
# Blog posts
# ------------------------------------------------------------------
blog_list = _generic_list(
    BlogPost, "doctor_admin/list.html", "Blog Yazıları",
    "doctor_admin:blog_add",
    "doctor_admin:blog_edit",
    "doctor_admin:blog_delete",
)
blog_add = _generic_edit(
    BlogPost, BlogPostForm, "doctor_admin:blog_list", "Yeni Blog Yazısı",
)
blog_edit = _generic_edit(
    BlogPost, BlogPostForm, "doctor_admin:blog_list", "Blog Yazısı Düzenle",
)
blog_delete = _generic_delete(BlogPost, "doctor_admin:blog_list")


# ------------------------------------------------------------------
# FAQ
# ------------------------------------------------------------------
faq_list = _generic_list(
    FAQItem, "doctor_admin/list.html", "SSS",
    "doctor_admin:faq_add",
    "doctor_admin:faq_edit",
    "doctor_admin:faq_delete",
)
faq_add = _generic_edit(
    FAQItem, FAQItemForm, "doctor_admin:faq_list", "Yeni SSS",
)
faq_edit = _generic_edit(
    FAQItem, FAQItemForm, "doctor_admin:faq_list", "SSS Düzenle",
)
faq_delete = _generic_delete(FAQItem, "doctor_admin:faq_list")


# ------------------------------------------------------------------
# Specialty areas (view + edit only — new ones require a slug & are
# technical enough to live in /admin/).
# ------------------------------------------------------------------
specialty_list = _generic_list(
    SpecialtyArea, "doctor_admin/list.html", "Uzmanlık Alanları",
    "doctor_admin:specialty_list",  # no add — direct to list
    "doctor_admin:specialty_edit",
    "doctor_admin:specialty_list",  # no delete — use /admin/
)
specialty_edit = _generic_edit(
    SpecialtyArea, SpecialtyAreaForm, "doctor_admin:specialty_list",
    "Uzmanlık Alanı Düzenle",
)


# ------------------------------------------------------------------
# Messages inbox
# ------------------------------------------------------------------
@doctor_required
def messages_inbox(request):
    qs = ContactMessage.objects.filter(is_archived=False).order_by("-created_at")
    return render(request, "doctor_admin/messages.html", {
        "messages_list": qs,
    })


@doctor_required
def message_detail(request, pk):
    m = get_object_or_404(ContactMessage, pk=pk)
    if not m.is_read:
        m.is_read = True
        m.save(update_fields=["is_read"])
    return render(request, "doctor_admin/message_detail.html", {"m": m})


@doctor_required
def message_archive(request, pk):
    m = get_object_or_404(ContactMessage, pk=pk)
    m.is_archived = True
    m.is_read = True
    m.save(update_fields=["is_archived", "is_read"])
    messages.success(request, "Mesaj arşivlendi.")
    return redirect("doctor_admin:messages")
