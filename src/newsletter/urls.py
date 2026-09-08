from django.urls import path

from .views import (
	AdminNewsletterCampaignView,
	AdminNewsletterDeleteView,
	AdminNewsletterListView,
	AdminNewsletterStatusView,
	PublicNewsletterSubscribeView,
)

urlpatterns = [
	path("newsletter", PublicNewsletterSubscribeView.as_view(), name="newsletter-subscribe"),
	path("admin/newsletter", AdminNewsletterListView.as_view(), name="admin-newsletter-list"),
	path(
		"admin/newsletter/campagnes",
		AdminNewsletterCampaignView.as_view(),
		name="admin-newsletter-campaigns",
	),
	path(
		"admin/newsletter/<int:pk>/statut",
		AdminNewsletterStatusView.as_view(),
		name="admin-newsletter-status",
	),
	path(
		"admin/newsletter/<int:pk>",
		AdminNewsletterDeleteView.as_view(),
		name="admin-newsletter-delete",
	),
]
