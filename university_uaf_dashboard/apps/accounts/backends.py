"""
Custom authentication backend for UAF Smart Dashboard.
Allows login via email or registration number.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOrRegistrationBackend(ModelBackend):
    """Authenticate using email or registration number."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None

        # Try email first
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Try registration number
            try:
                user = User.objects.get(registration_number=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
