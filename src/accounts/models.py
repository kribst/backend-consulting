from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class AdminUserManager(BaseUserManager):
	def create_user(self, email, password=None, **extra_fields):
		if not email:
			raise ValueError("L'adresse email est obligatoire.")
		user = self.model(email=self.normalize_email(email), **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password=None, **extra_fields):
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("role", AdminUser.Role.ADMIN)
		return self.create_user(email, password, **extra_fields)


class AdminUser(AbstractBaseUser, PermissionsMixin):
	class Role(models.TextChoices):
		ADMIN = "admin", "Administrateur"

	nom = models.CharField(max_length=150)
	email = models.EmailField(unique=True)
	role = models.CharField(max_length=30, choices=Role.choices, default=Role.ADMIN)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	date_joined = models.DateTimeField(auto_now_add=True)

	objects = AdminUserManager()

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ["nom"]

	def __str__(self):
		return self.email
