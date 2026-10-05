from django.conf import settings
from rest_framework import serializers

from .models import Actualite, Service, SiteContent, Testimonial, TeamMember

MAX_IMAGE_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/avif",
}


def build_media_url(serializer, obj):
    """Retourne une URL exploitable pour une image téléchargée, sans convertir des assets publics en URL media."""
    image = getattr(obj, "image", None)
    if not image:
        return None

    image_name = getattr(image, "name", None) or str(image)
    if not image_name:
        return None
    image_name = image_name.replace("\\", "/").strip()

    if not image_name or image_name.startswith("/"):
        return None

    normalized = image_name.lstrip('/')
    media_path = f"{settings.MEDIA_URL}{normalized}"

    request = serializer.context.get("request")
    if request:
        return request.build_absolute_uri(media_path)
    return media_path


class ActualiteSerializer(serializers.ModelSerializer):
    # L'image est téléversée via l'endpoint d'upload et arrive ici sous forme
    # de chemin média relatif, pas de binaire : on la lit comme une chaîne.
    image = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Actualite
        fields = (
            "id",
            "slug",
            "title",
            "category",
            "datePublication",
            "heurePublication",
            "image",
            "image_url",
            "imageAlt",
            "content",
            "position",
        )
        read_only_fields = ("id", "image_url")

    def get_image_url(self, obj):
        return build_media_url(self, obj)


class ServiceSerializer(serializers.ModelSerializer):
    # L'image est téléversée via POST /admin/services/upload-image et arrive
    # ici sous forme de chemin média relatif, pas de binaire.
    image = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            "id",
            "title",
            "slug",
            "icon",
            "summary",
            "description",
            "image",
            "image_url",
            "imageAlt",
            "keyPoints",
            "includes",
            "audience",
            "benefits",
            "useCases",
            "process",
            "relatedSlugs",
            "position",
        )
        read_only_fields = ("id", "image_url")

    def get_image_url(self, obj):
        return build_media_url(self, obj)


class SiteContentSerializer(serializers.ModelSerializer):
    processSteps = serializers.JSONField(source="process_steps", required=False)

    class Meta:
        model = SiteContent
        fields = (
            "company",
            "services",
            "actualites",
            "statistics",
            "testimonials",
            "processSteps",
            "seo",
        )

    def create(self, validated_data):
        return SiteContent.objects.create(**validated_data)


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ("id", "name", "role", "quote", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class TeamMemberSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = ("id", "name", "poste", "image", "image_url", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def get_image_url(self, obj):
        return build_media_url(self, obj)


class ServiceImageUploadSerializer(serializers.Serializer):
    """Valide le fichier image téléversé depuis l'interface d'administration."""

    image = serializers.ImageField(required=True)

    def validate_image(self, value):
        if value.size > MAX_IMAGE_UPLOAD_BYTES:
            raise serializers.ValidationError(
                f"Image trop lourde ({value.size // 1024} Ko). Maximum : {MAX_IMAGE_UPLOAD_BYTES // (1024 * 1024)} Mo."
            )

        content_type = (getattr(value, "content_type", "") or "").lower()
        if content_type and content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise serializers.ValidationError(
                "Format non supporté. Utilisez JPG, PNG, WEBP, GIF ou AVIF."
            )

        return value
