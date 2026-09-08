from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SiteContent, Testimonial, TeamMember
from .serializers import SiteContentSerializer, TestimonialSerializer, TeamMemberSerializer

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
			return Response({"data": {"statistics": DEFAULT_STATISTICS}})
		return Response({"data": SiteContentSerializer(content).data})


class AdminSiteContentView(APIView):
	permission_classes = [IsAuthenticated]

	def put(self, request):
		content = SiteContent.objects.first()
		serializer = SiteContentSerializer(content, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		content = serializer.save() if content else SiteContent.objects.create(**serializer.validated_data)
		return Response({"data": SiteContentSerializer(content).data})


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
