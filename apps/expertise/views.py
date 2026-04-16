from django.shortcuts import get_object_or_404, render

from .models import SpecialtyArea, SpecialtyCategory


def specialty_list(request):
    categories = SpecialtyCategory.objects.prefetch_related("areas").order_by("order")
    areas = SpecialtyArea.objects.select_related("category").order_by("order")
    uncategorized = areas.filter(category__isnull=True)
    return render(request, "expertise/list.html", {
        "categories": categories,
        "all_areas": areas,
        "uncategorized": uncategorized,
    })


def specialty_detail(request, slug):
    area = get_object_or_404(SpecialtyArea, slug=slug)
    related = (
        SpecialtyArea.objects.filter(category=area.category)
        .exclude(pk=area.pk)
        .order_by("order")[:3]
    )
    related_posts = area.blog_posts.filter(status="published").order_by("-published_at")[:3]
    related_faqs = area.faq_items.order_by("order")[:5]
    return render(request, "expertise/detail.html", {
        "area": area,
        "related": related,
        "related_posts": related_posts,
        "related_faqs": related_faqs,
    })
