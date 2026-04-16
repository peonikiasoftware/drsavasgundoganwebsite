from django.http import HttpResponse


def post_list(request):
    return HttpResponse("stub")


def post_detail(request, slug):
    return HttpResponse(f"stub:{slug}")
