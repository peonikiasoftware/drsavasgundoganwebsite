"""Doctor-friendly admin dashboard (/doctor-admin/)."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator

from apps.blog.models import BlogPost
from apps.core.models import ContactMessage, DoctorProfile
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
    return render(request, "doctor_admin/dashboard.html", {
        "unread_messages": unread_messages,
        "recent_messages": recent_messages,
        "stats": stats,
        "doctor": DoctorProfile.load(),
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
