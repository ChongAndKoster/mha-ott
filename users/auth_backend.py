from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

from .models import CustomUser


class PasswordlessAuthBackend(ModelBackend):
    """Log in to Django without providing a password.
    """
    def authenticate(self, request, username=None):
        try:
            return CustomUser.objects.get(username=username)
            print('Authenticated user: {}'.format(username))
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None