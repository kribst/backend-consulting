from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ("nom", "email", "sujet", "statut", "created_at")
	list_filter = ("statut", "created_at")
	search_fields = ("nom", "email", "entreprise", "sujet")
