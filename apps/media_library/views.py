from django.shortcuts import render

from .models import Video, VideoCategory


def video_list(request):
    videos = Video.objects.select_related("category").all()
    category_slug = request.GET.get("category")
    if category_slug:
        videos = videos.filter(category__slug=category_slug)

    categories = VideoCategory.objects.filter(videos__isnull=False).distinct().order_by("order")
    # Featured hero for the Videos page: prefer the Acıbadem Instagram Reel —
    # consistent with the home page hero.
    hero_video = (
        Video.objects.filter(platform="instagram", is_official_acibadem=True)
        .order_by("-is_featured", "order").first()
        or Video.objects.filter(is_official_acibadem=True)
        .order_by("-is_featured", "order").first()
    )

    return render(request, "media_library/list.html", {
        "videos": videos,
        "categories": categories,
        "hero_video": hero_video,
        "current_category": category_slug or "",
    })
