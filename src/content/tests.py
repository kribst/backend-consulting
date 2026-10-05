from io import BytesIO
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from rest_framework.test import APIClient

from .models import Actualite, Service, SiteContent


class SiteContentActualitesTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_public_endpoint_returns_default_actualites(self):
		response = self.client.get("/api/site-content")

		self.assertEqual(response.status_code, 200)
		actualites = response.json()["data"]["actualites"]
		self.assertEqual(len(actualites), 3)
		self.assertEqual(actualites[0]["slug"], "signature-convention-partenariat")

	def test_public_endpoint_preserves_an_intentionally_empty_actualites_list(self):
		Actualite.objects.all().delete()

		response = self.client.get("/api/site-content")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["data"]["actualites"], [])

	def test_public_actualite_serializes_uploaded_and_static_images_correctly(self):
		response = self.client.get("/api/site-content")

		self.assertEqual(response.status_code, 200)
		actualite = response.json()["data"]["actualites"][0]
		self.assertEqual(actualite["image"], "/images/cooperation.jpg")
		self.assertIsNone(actualite["image_url"])

	def test_actualite_image_upload_stores_file_under_images_actualites(self):
		user = get_user_model().objects.create_user(
			email="actualite-admin@example.test",
			password="test-password",
			nom="Administrateur actualités",
		)
		self.client.force_authenticate(user=user)
		image_buffer = BytesIO()
		Image.new("RGB", (1, 1), color="white").save(image_buffer, format="PNG")
		uploaded_image = SimpleUploadedFile("publication.png", image_buffer.getvalue(), content_type="image/png")

		with tempfile.TemporaryDirectory() as media_root:
			with override_settings(MEDIA_ROOT=media_root):
				response = self.client.post(
					"/api/admin/actualites/upload-image",
					{"image": uploaded_image},
					format="multipart",
				)

				self.assertEqual(response.status_code, 201, response.content)
				stored_path = response.json()["data"]["image"]
				self.assertTrue(stored_path.startswith("images/actualites/"))
				self.assertTrue(default_storage.exists(stored_path))
				self.assertTrue((Path(media_root) / stored_path).is_file())

		self.assertTrue(response.json()["data"]["image_url"].endswith(f"/media/{stored_path}"))


class SiteContentServicesTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_public_endpoint_returns_migrated_default_services(self):
		response = self.client.get("/api/site-content")

		self.assertEqual(response.status_code, 200)
		services = response.json()["data"]["services"]
		self.assertEqual(len(services), 12)
		self.assertEqual(services[0]["slug"], "conseil-juridique-et-fiscal")
		self.assertIn("keyPoints", services[0])
		self.assertEqual(services[0]["image"], "/images/juridique-fiscal.jpg")
		self.assertIsNone(services[0]["image_url"])

	def test_deleting_all_services_is_reflected_by_public_endpoint(self):
		Service.objects.all().delete()

		response = self.client.get("/api/site-content")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["data"]["services"], [])

	def test_admin_saves_service_fields_and_uploaded_image_path_to_database(self):
		user = get_user_model().objects.create_user(
			email="service-admin@example.test",
			password="test-password",
			nom="Administrateur services",
		)
		self.client.force_authenticate(user=user)
		image_path = "images/services/consulting-12345678.png"

		response = self.client.put(
			"/api/admin/site-content",
			{
				"services": [
					{
						"title": "Conseil personnalisé",
						"slug": "conseil-personnalise",
						"icon": "briefcase-business",
						"summary": "Résumé du service.",
						"description": "Description détaillée.",
						"image": image_path,
						"imageAlt": "Équipe de conseil",
						"keyPoints": ["Diagnostic"],
						"includes": ["Accompagnement"],
						"audience": ["Entreprises"],
						"benefits": ["Meilleure organisation"],
						"useCases": ["Développement"],
						"process": ["Analyse"],
						"relatedSlugs": [],
					}
				]
			},
			format="json",
		)

		self.assertEqual(response.status_code, 200, response.content)
		service = Service.objects.get(slug="conseil-personnalise")
		self.assertEqual(service.title, "Conseil personnalisé")
		self.assertEqual(service.image.name, image_path)
		self.assertEqual(response.json()["data"]["services"][0]["image"], image_path)
		self.assertEqual(
			response.json()["data"]["services"][0]["image_url"],
			f"http://testserver/media/{image_path}",
		)

	def test_service_image_upload_stores_file_under_images_services(self):
		user = get_user_model().objects.create_user(
			email="image-admin@example.test",
			password="test-password",
			nom="Administrateur images",
		)
		self.client.force_authenticate(user=user)
		image_buffer = BytesIO()
		Image.new("RGB", (1, 1), color="white").save(image_buffer, format="PNG")
		uploaded_image = SimpleUploadedFile("consulting.png", image_buffer.getvalue(), content_type="image/png")
		with tempfile.TemporaryDirectory() as media_root:
			with override_settings(MEDIA_ROOT=media_root):
				response = self.client.post(
					"/api/admin/services/upload-image",
					{"image": uploaded_image},
					format="multipart",
				)

				self.assertEqual(response.status_code, 201, response.content)
				stored_path = response.json()["data"]["image"]
				self.assertTrue(stored_path.startswith("images/services/"))
				self.assertTrue(default_storage.exists(stored_path))
				self.assertTrue((Path(media_root) / stored_path).is_file())

		self.assertTrue(
			response.json()["data"]["image_url"].endswith(f"/media/{stored_path}")
		)
