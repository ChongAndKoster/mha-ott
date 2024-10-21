from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
	username = models.CharField(_('username'), max_length = 150, unique=True)
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_new_user = models.BooleanField(default=True)

	date_joined = models.DateTimeField(default=timezone.now)

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = []

	objects = CustomUserManager()

	def __str__(self):
		return self.username