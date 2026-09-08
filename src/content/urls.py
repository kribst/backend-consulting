from django.urls import path

from .views import AdminSiteContentView, AdminTeamDetailView, AdminTeamListView, AdminTestimonialDetailView, AdminTestimonialListView, PublicTestimonialListView, SiteContentView, TeamListView

urlpatterns = [
    path("site-content", SiteContentView.as_view(), name="site-content"),
    path("admin/site-content", AdminSiteContentView.as_view(), name="admin-site-content"),
    path("admin/testimonials", AdminTestimonialListView.as_view(), name="admin-testimonials"),
    path("admin/testimonials/<int:pk>", AdminTestimonialDetailView.as_view(), name="admin-testimonial-detail"),
    path("testimonials", PublicTestimonialListView.as_view(), name="public-testimonials"),
    path("team", TeamListView.as_view(), name="public-team"),
    path("admin/team", AdminTeamListView.as_view(), name="admin-team"),
    path("admin/team/<int:pk>", AdminTeamDetailView.as_view(), name="admin-team-detail"),
]
