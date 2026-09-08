from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import AdminUserSerializer, LoginSerializer


def error_response(message, http_status=status.HTTP_400_BAD_REQUEST):
	return Response({"message": message}, status=http_status)


class LoginView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		if not serializer.is_valid():
			return error_response("Email et mot de passe sont obligatoires.")

		user = authenticate(
			request=request,
			email=serializer.validated_data["email"],
			password=serializer.validated_data["password"],
		)
		if user is None:
			return error_response("Identifiants admin incorrects.", status.HTTP_401_UNAUTHORIZED)

		refresh = RefreshToken.for_user(user)
		return Response({
			"token": str(refresh.access_token),
			"refresh_token": str(refresh),
			"utilisateur": AdminUserSerializer(user).data,
		})


class MeView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return Response({"utilisateur": AdminUserSerializer(request.user).data})


class LogoutView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		return Response({"message": "Déconnexion réussie."})

# Create your views here.
