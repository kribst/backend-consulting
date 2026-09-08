from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views.static import serve
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/", include("messages.urls")),
    path("api/", include("newsletter.urls")),
    path("api/", include("content.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=BASE_DIR / "static")
else:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
