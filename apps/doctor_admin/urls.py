from django.urls import path

from . import views

app_name = "doctor_admin"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.DoctorLoginView.as_view(), name="login"),
    path("logout/", views.DoctorLogoutView.as_view(), name="logout"),

    path("profile/", views.profile_edit, name="profile"),

    path("messages/", views.messages_inbox, name="messages"),
    path("messages/<int:pk>/", views.message_detail, name="message_detail"),
    path("messages/<int:pk>/archive/", views.message_archive, name="message_archive"),

    # Education
    path("education/", views.education_list, name="education_list"),
    path("education/add/", views.education_add, name="education_add"),
    path("education/<int:pk>/edit/", views.education_edit, name="education_edit"),
    path("education/<int:pk>/delete/", views.education_delete, name="education_delete"),

    # Experience
    path("experience/", views.experience_list, name="experience_list"),
    path("experience/add/", views.experience_add, name="experience_add"),
    path("experience/<int:pk>/edit/", views.experience_edit, name="experience_edit"),
    path("experience/<int:pk>/delete/", views.experience_delete, name="experience_delete"),

    # Membership
    path("membership/", views.membership_list, name="membership_list"),
    path("membership/add/", views.membership_add, name="membership_add"),
    path("membership/<int:pk>/edit/", views.membership_edit, name="membership_edit"),
    path("membership/<int:pk>/delete/", views.membership_delete, name="membership_delete"),

    # Publications
    path("publications/", views.publication_list, name="publication_list"),
    path("publications/add/", views.publication_add, name="publication_add"),
    path("publications/<int:pk>/edit/", views.publication_edit, name="publication_edit"),
    path("publications/<int:pk>/delete/", views.publication_delete, name="publication_delete"),

    # Videos
    path("videos/", views.video_list, name="video_list"),
    path("videos/add/", views.video_add, name="video_add"),
    path("videos/<int:pk>/edit/", views.video_edit, name="video_edit"),
    path("videos/<int:pk>/delete/", views.video_delete, name="video_delete"),

    # Blog
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/add/", views.blog_add, name="blog_add"),
    path("blog/<int:pk>/edit/", views.blog_edit, name="blog_edit"),
    path("blog/<int:pk>/delete/", views.blog_delete, name="blog_delete"),

    # FAQ
    path("faq/", views.faq_list, name="faq_list"),
    path("faq/add/", views.faq_add, name="faq_add"),
    path("faq/<int:pk>/edit/", views.faq_edit, name="faq_edit"),
    path("faq/<int:pk>/delete/", views.faq_delete, name="faq_delete"),

    # Specialty areas (edit-only — list then edit)
    path("specialty/", views.specialty_list, name="specialty_list"),
    path("specialty/<int:pk>/edit/", views.specialty_edit, name="specialty_edit"),
]
