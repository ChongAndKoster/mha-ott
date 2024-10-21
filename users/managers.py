from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
	"""
	Custom user model manager where username is the unique identifiers
	for authentication instead of usernames.
	"""
	def create_user(self, username, **extra_fields):
		"""
		Create and save a User with the given username and password.
		"""
		if not username:
			raise ValueError(_('The username must be set'))
		# username = self.normalize_username(username)
		user = self.model(username=username, **extra_fields)
		# user.set_password(password)
		user.save()
		return user

	def create_superuser(self, username, password, **extra_fields):
		"""
		Create and save a SuperUser with the given username and password.
		"""
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_active', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError(_('Superuser must have is_staff=True.'))
		if extra_fields.get('is_superuser') is not True:
			raise ValueError(_('Superuser must have is_superuser=True.'))
		
		user = self.model(username=username, **extra_fields)
		user.set_password(password)
		user.save()
		
		return user