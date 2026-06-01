from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    """Permite iniciar sesión usando el correo electrónico en lugar de un username"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        # Si no pasan username, buscamos por el correo inyectado
        email = kwargs.get('email', username)
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None