from django.shortcuts import render

from .models import FAQCategory, FAQItem


def faq_list(request):
    categories = FAQCategory.objects.prefetch_related("items").order_by("order")
    uncategorized = FAQItem.objects.filter(category__isnull=True).order_by("order")
    featured = FAQItem.objects.filter(is_featured=True).order_by("order")
    return render(request, "faq/list.html", {
        "categories": categories,
        "uncategorized": uncategorized,
        "featured": featured,
    })
