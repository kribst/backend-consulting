from django.contrib import admin
from django.utils.html import format_html

from .models import SiteContent, Testimonial, TeamMember


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
	list_display = ("id", "updated_at")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
	list_display = ("name", "role", "quote", "created_at")
	search_fields = ("name", "role", "quote")
	list_filter = ("created_at",)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
	list_display = ("id", "image_tag", "name", "poste", "created_at", "updated_at")
	list_display_links = ("id", "name")
	search_fields = ("name", "poste")
	list_filter = ("created_at", "updated_at")
	readonly_fields = ("created_at", "updated_at", "image_preview")
	ordering = ("id",)
	fieldsets = (
		(None, {
			"fields": ("name", "poste", "image", "image_preview"),
		}),
		("Métadonnées", {
			"classes": ("collapse",),
			"fields": ("created_at", "updated_at"),
		}),
	)

	def image_tag(self, obj):
		if obj.image:
			return format_html('<img src="{}" style="height: 40px; width: 40px; object-fit: cover; border-radius: 6px;" />', obj.image.url)
		return format_html('<span style="color: #9ca3af;">—</span>')
	image_tag.short_description = "Image"

	def image_preview(self, obj):
		if obj.image:
			return format_html(
				'<img src="{}" style="max-height: 220px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.15);" />',
				obj.image.url,
			)
		return format_html('<span style="color: #9ca3af;">Aucune image</span>')
	image_preview.short_description = "Aperçu"
