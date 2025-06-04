from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email__iexact=username)  # Игнорируем регистр
            print(f"Found user: {user}")  # Отладка
        except UserModel.DoesNotExist:
            print("User not found")  # Отладка
            return None
        if user.check_password(password):
            print("Password check passed")  # Отладка
            return user
        print("Password check failed")  # Отладка
        return None