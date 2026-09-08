from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AdminUser


@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
	model = AdminUser
	ordering = ("email",)
	list_display = ("email", "nom", "role", "is_staff", "is_active")
	fieldsets = (
		(None, {"fields": ("email", "password")}),
		("Identite", {"fields": ("nom", "role")}),
		("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
		("Dates", {"fields": ("last_login",)}),
	)
	add_fieldsets = (
		(None, {"classes": ("wide",), "fields": ("email", "nom", "password1", "password2", "is_staff", "is_active")}),
	)
	search_fields = ("email", "nom")





admin.site.site_header = "ADMINISTRATION FALKAOH CONSULTING"
admin.site.site_title = "FALKAOH CONSULTING"  # Browser tab title
admin.site.site_url = "https://falkaohafriconsulting.com/"  # Remplacez par l'URL de votre front React
admin.site.index_title = "Tableau de Bord FALKAOH CONSULTING"  # Admin index page title