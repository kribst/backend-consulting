from rest_framework import serializers

from content.models import SiteContent

from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = (
            "id",
            "nom",
            "email",
            "telephone",
            "entreprise",
            "service_id",
            "service",
            "sujet",
            "message",
            "statut",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "service", "statut", "created_at", "updated_at")


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    service = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ContactMessage
        fields = (
            "nom",
            "email",
            "telephone",
            "entreprise",
            "service_id",
            "service",
            "sujet",
            "message",
        )

    def create(self, validated_data):
        service_id = validated_data.get("service_id")
        site_content = SiteContent.objects.first()
        if site_content and service_id is not None:
            selected_service = next(
                (
                    service for service in site_content.services
                    if str(service.get("id")) == str(service_id)
                ),
                None,
            )
            if selected_service:
                validated_data["service"] = selected_service.get("title", "")
        return ContactMessage.objects.create(**validated_data)


class ContactMessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ("statut",)

class ContactMessageReplySerializer(serializers.Serializer):
    sujet = serializers.CharField(max_length=255)
    message = serializers.CharField()
