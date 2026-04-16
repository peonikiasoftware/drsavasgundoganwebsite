from django.shortcuts import render

from .models import Education, Experience, Membership


def timeline(request):
    return render(request, "experience/timeline.html", {
        "educations": Education.objects.all(),
        "experiences": Experience.objects.all(),
        "memberships": Membership.objects.all(),
    })
