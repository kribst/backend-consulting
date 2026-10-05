import os
import re
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils.text import slugify
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Actualite, Service, SiteContent, Testimonial, TeamMember
from .serializers import (
    ActualiteSerializer,
    ServiceImageUploadSerializer,
    ServiceSerializer,
    SiteContentSerializer,
    TestimonialSerializer,
    TeamMemberSerializer,
)

DEFAULT_STATISTICS = [
    {"label": "Experts", "value": "6", "description": "profils mobilisables selon les missions"},
    {"label": "Clients satisfaits", "value": "39", "description": "organisations accompagnées avec rigueur"},
    {"label": "Missions réalisées", "value": "19", "description": "interventions structurées et documentées"},
    {"label": "Parcours formation", "value": "8", "description": "programmes adaptés aux équipes"},
]


class SiteContentView(APIView):
	permission_classes = [AllowAny]

	def get(self, request):
		content = SiteContent.objects.first()
		if content is None:
			data = {"statistics": DEFAULT_STATISTICS}
		else:
			data = SiteContentSerializer(content).data
		data["actualites"] = ActualiteSerializer(Actualite.objects.all(), many=True, context={"request": request}).data
		data["services"] = ServiceSerializer(Service.objects.all(), many=True, context={"request": request}).data
		return Response({"data": data})


class AdminSiteContentView(APIView):
	permission_classes = [IsAuthenticated]

	def put(self, request):
		content = SiteContent.objects.first()
		serializer = SiteContentSerializer(content, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		actualites = serializer.validated_data.get("actualites")
		services = serializer.validated_data.get("services")
		content = serializer.save() if content else SiteContent.objects.create(**serializer.validated_data)

		if actualites is not None or services is not None:
			with transaction.atomic():
				if actualites is not None:
					retained_ids = []
					for position, item in enumerate(actualites):
						if not isinstance(item, dict):
							continue
						instance = Actualite.objects.filter(pk=item.get("id")).first() if item.get("id") else None
						if instance is None and item.get("slug"):
							instance = Actualite.objects.filter(slug=item["slug"]).first()
						article_data = {**item, "position": position}
						article_serializer = ActualiteSerializer(instance, data=article_data)
						article_serializer.is_valid(raise_exception=True)
						retained_ids.append(article_serializer.save().pk)
					Actualite.objects.exclude(pk__in=retained_ids).delete()

				if services is not None:
					retained_ids = []
					for position, item in enumerate(services):
						if not isinstance(item, dict):
							continue
						instance = Service.objects.filter(pk=item.get("id")).first() if item.get("id") else None
						if instance is None and item.get("slug"):
							instance = Service.objects.filter(slug=item["slug"]).first()
						service_data = {**item, "position": position}
						service_serializer = ServiceSerializer(instance, data=service_data)
						service_serializer.is_valid(raise_exception=True)
						retained_ids.append(service_serializer.save().pk)
					Service.objects.exclude(pk__in=retained_ids).delete()

		data = SiteContentSerializer(content).data
		data["actualites"] = ActualiteSerializer(Actualite.objects.all(), many=True, context={"request": request}).data
		data["services"] = ServiceSerializer(Service.objects.all(), many=True, context={"request": request}).data
		return Response({"data": data})


class AdminTestimonialListView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		testimonials = Testimonial.objects.all()
		serializer = TestimonialSerializer(testimonials, many=True)
		return Response({"data": serializer.data})

	def post(self, request):
		serializer = TestimonialSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"data": serializer.data}, status=201)


class AdminTestimonialDetailView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, pk):
		testimonial = Testimonial.objects.filter(pk=pk).first()
		if not testimonial:
			return Response({"detail": "Témoignage introuvable."}, status=404)
		serializer = TestimonialSerializer(testimonial)
		return Response({"data": serializer.data})

	def put(self, request, pk):
		testimonial = Testimonial.objects.filter(pk=pk).first()
		if not testimonial:
			return Response({"detail": "Témoignage introuvable."}, status=404)
		serializer = TestimonialSerializer(testimonial, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"data": serializer.data})

	def delete(self, request, pk):
		testimonial = Testimonial.objects.filter(pk=pk).first()
		if not testimonial:
			return Response({"detail": "Témoignage introuvable."}, status=404)
		testimonial.delete()
		return Response(status=204)


class PublicTestimonialListView(APIView):
	permission_classes = [AllowAny]

	def get(self, request):
		testimonials = Testimonial.objects.all().order_by("-created_at")
		serializer = TestimonialSerializer(testimonials, many=True)
		return Response({"data": serializer.data})


class TeamListView(APIView):
	permission_classes = [AllowAny]

	def get(self, request):
		members = TeamMember.objects.all()
		serializer = TeamMemberSerializer(members, many=True, context={'request': request})
		return Response({"data": serializer.data})


class AdminTeamListView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		members = TeamMember.objects.all()
		serializer = TeamMemberSerializer(members, many=True, context={'request': request})
		return Response({"data": serializer.data})

	def post(self, request):
		serializer = TeamMemberSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"data": serializer.data}, status=201)


class AdminTeamDetailView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, pk):
		member = TeamMember.objects.filter(pk=pk).first()
		if not member:
			return Response({"detail": "Membre introuvable."}, status=404)
		serializer = TeamMemberSerializer(member, context={'request': request})
		return Response({"data": serializer.data})

	def put(self, request, pk):
		member = TeamMember.objects.filter(pk=pk).first()
		if not member:
			return Response({"detail": "Membre introuvable."}, status=404)
		serializer = TeamMemberSerializer(member, data=request.data, partial=True, context={'request': request})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"data": serializer.data})

	def delete(self, request, pk):
		member = TeamMember.objects.filter(pk=pk).first()
		if not member:
			return Response({"detail": "Membre introuvable."}, status=404)
		member.delete()
		return Response(status=204)


CONTENT_TYPE_EXTENSIONS = {
	"image/jpeg": ".jpg",
	"image/png": ".png",
	"image/webp": ".webp",
	"image/gif": ".gif",
	"image/avif": ".avif",
}


def build_uploaded_image_name(uploaded_file):
	"""Construit un nom de fichier sûr et unique pour une image téléversée."""
	original_name = os.path.basename(uploaded_file.name or "")
	stem, extension = os.path.splitext(original_name)

	extension = re.sub(r"[^a-z0-9.]", "", extension.lower())[:10]
	if not extension:
		content_type = (getattr(uploaded_file, "content_type", "") or "").lower()
		extension = CONTENT_TYPE_EXTENSIONS.get(content_type, ".jpg")

	stem = slugify(stem)[:60] or "image"

	return f"{stem}-{uuid.uuid4().hex[:8]}{extension}"


class AdminServiceImageUploadView(APIView):
	"""Enregistre une image téléversée pour un service et renvoie son chemin média."""

	permission_classes = [IsAuthenticated]
	parser_classes = [MultiPartParser, FormParser]

	def post(self, request):
		serializer = ServiceImageUploadSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		image = serializer.validated_data["image"]
		stored_path = default_storage.save(f"images/services/{build_uploaded_image_name(image)}", image)
		image_url = request.build_absolute_uri(f"{settings.MEDIA_URL}{stored_path}")

		return Response(
			{"data": {"image": stored_path, "image_url": image_url}},
			status=201,
		)


class AdminActualiteImageUploadView(APIView):
	"""Enregistre une image téléversée pour une actualité dans MEDIA_ROOT."""

	permission_classes = [IsAuthenticated]
	parser_classes = [MultiPartParser, FormParser]

	def post(self, request):
		serializer = ServiceImageUploadSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		image = serializer.validated_data["image"]
		stored_path = default_storage.save(f"images/actualites/{build_uploaded_image_name(image)}", image)
		image_url = request.build_absolute_uri(f"{settings.MEDIA_URL}{stored_path}")

		return Response(
			{"data": {"image": stored_path, "image_url": image_url}},
			status=201,
		)
