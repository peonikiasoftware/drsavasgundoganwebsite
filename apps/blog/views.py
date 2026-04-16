from django.db.models import F
from django.shortcuts import get_object_or_404, render

from .models import BlogCategory, BlogPost


def post_list(request):
    posts = BlogPost.objects.filter(status="published").select_related("category").order_by("-published_at")
    category_slug = request.GET.get("category")
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    q = request.GET.get("q", "").strip()
    if q:
        posts = posts.filter(title__icontains=q)

    categories = BlogCategory.objects.all().order_by("order")
    featured = BlogPost.objects.filter(status="published", is_featured=True).first()

    return render(request, "blog/list.html", {
        "posts": posts,
        "categories": categories,
        "current_category": category_slug or "",
        "q": q,
        "featured": featured,
    })


def post_detail(request, slug):
    post = get_object_or_404(
        BlogPost.objects.select_related("category", "related_specialty"),
        slug=slug, status="published",
    )
    BlogPost.objects.filter(pk=post.pk).update(view_count=F("view_count") + 1)
    related = BlogPost.objects.filter(
        status="published", category=post.category,
    ).exclude(pk=post.pk).order_by("-published_at")[:3]
    return render(request, "blog/detail.html", {
        "post": post, "related": related,
    })
