from django.urls import path

from .views import (
    AdminDashboardView,
    AdminMessageDeleteView,
    AdminMessageDetailView,
    AdminMessageListView,
    AdminMessageReplyView,
    AdminMessageStatusView,
    PublicContactMessageView,
)

urlpatterns = [
    path("messages-contact", PublicContactMessageView.as_view(), name="contact-message-create"),
    path("admin/dashboard", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("admin/messages-contact", AdminMessageListView.as_view(), name="admin-message-list"),
    path("admin/messages-contact/<int:pk>", AdminMessageDetailView.as_view(), name="admin-message-detail"),
    path("admin/messages-contact/<int:pk>/statut", AdminMessageStatusView.as_view(), name="admin-message-status"),
    path("admin/messages-contact/<int:pk>/reply", AdminMessageReplyView.as_view(), name="admin-message-reply"),
    path("admin/messages-contact/<int:pk>/supprimer", AdminMessageDeleteView.as_view(), name="admin-message-delete"),
]
