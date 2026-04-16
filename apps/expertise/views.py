from django.http import HttpResponse


def _stub(request, *a, **kw):
    return HttpResponse("stub")


specialty_list = _stub
specialty_detail = _stub
