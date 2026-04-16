"""Core views — placeholder; real ones land in Phase 6."""
from django.http import HttpResponse
from django.shortcuts import render


def _stub(request, slug="home"):
    return HttpResponse(f"stub:{slug}")


home = _stub
about = _stub
contact = _stub
privacy = _stub
kvkk = _stub


def custom_404(request, exception):
    return render(request, "errors/404.html", status=404)


def custom_500(request):
    return render(request, "errors/500.html", status=500)
