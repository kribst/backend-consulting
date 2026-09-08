from django.conf import settings
from rest_framework import serializers

from .models import SiteContent, Testimonial, TeamMember


class SiteContentSerializer(serializers.ModelSerializer):
    processSteps = serializers.JSONField(source="process_steps", required=False)

    class Meta:
        model = SiteContent
        fields = (
            "company",
            "services",
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
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(settings.MEDIA_URL + obj.image.name)
            return f"{settings.MEDIA_URL}{obj.image.name}"
        return None
