from django.db.models import Sum
from django.shortcuts import render

from .models import Publication


def publication_list(request):
    qs = Publication.objects.all()

    year = request.GET.get("year")
    journal = request.GET.get("journal")
    sort = request.GET.get("sort", "year")

    if year and year.isdigit():
        qs = qs.filter(year=int(year))
    if journal:
        qs = qs.filter(journal=journal)

    if sort == "citations":
        qs = qs.order_by("-citation_count", "-year")
    else:
        qs = qs.order_by("-year", "-citation_count")

    years = Publication.objects.values_list("year", flat=True).distinct().order_by("-year")
    journals = Publication.objects.values_list("journal", flat=True).distinct().order_by("journal")
    totals = Publication.objects.aggregate(total_citations=Sum("citation_count"))

    return render(request, "publications/list.html", {
        "publications": qs,
        "years": years,
        "journals": journals,
        "current_year": year or "",
        "current_journal": journal or "",
        "current_sort": sort,
        "total_count": Publication.objects.count(),
        "total_citations": totals["total_citations"] or 0,
    })
