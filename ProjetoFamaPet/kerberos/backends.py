from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        user_model = get_user_model()
        try:
            user = user_model._default_manager.get(email__iexact=username)
        except user_model.DoesNotExist:
            return super().authenticate(
                request, username=username, password=password, **kwargs
            )
        except user_model.MultipleObjectsReturned:
            user_model().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None