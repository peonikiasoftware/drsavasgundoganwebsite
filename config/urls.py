"""Root URL configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path(settings.ADMIN_URL_PATH, admin.site.urls),
    path("doctor-admin/", include("apps.doctor_admin.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("robots.txt", RedirectView.as_view(url="/static/robots.txt", permanent=True)),
]

urlpatterns += i18n_patterns(
    path("", include("apps.core.urls")),
    path("uzmanlik/", include("apps.expertise.urls")),
    path("kariyer/", include("apps.experience.urls")),
    path("yayinlar/", include("apps.publications.urls")),
    path("videolar/", include("apps.media_library.urls")),
    path("blog/", include("apps.blog.urls")),
    path("sss/", include("apps.faq.urls")),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar  # noqa: F401
        urlpatterns = [path("__debug__/", include("debug_toolbar.urls"))] + urlpatterns
    except ImportError:
        pass

handler404 = "apps.core.views.custom_404"
handler500 = "apps.core.views.custom_500"
