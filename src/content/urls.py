from django.urls import path

from .views import (
    AdminServiceImageUploadView,
    AdminActualiteImageUploadView,
    AdminSiteContentView,
    AdminTeamDetailView,
    AdminTeamListView,
    AdminTestimonialDetailView,
    AdminTestimonialListView,
    PublicTestimonialListView,
    SiteContentView,
    TeamListView,
)

urlpatterns = [
    path("site-content", SiteContentView.as_view(), name="site-content"),
    path("admin/site-content", AdminSiteContentView.as_view(), name="admin-site-content"),
    path("admin/services/upload-image", AdminServiceImageUploadView.as_view(), name="admin-service-upload-image"),
    path("admin/actualites/upload-image", AdminActualiteImageUploadView.as_view(), name="admin-actualite-upload-image"),
    path("admin/testimonials", AdminTestimonialListView.as_view(), name="admin-testimonials"),
    path("admin/testimonials/<int:pk>", AdminTestimonialDetailView.as_view(), name="admin-testimonial-detail"),
    path("testimonials", PublicTestimonialListView.as_view(), name="public-testimonials"),
    path("team", TeamListView.as_view(), name="public-team"),
    path("admin/team", AdminTeamListView.as_view(), name="admin-team"),
    path("admin/team/<int:pk>", AdminTeamDetailView.as_view(), name="admin-team-detail"),
]
