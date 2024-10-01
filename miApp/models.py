from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Manager personalizado para el modelo de usuario
class CustomUserManager(BaseUserManager):
    def create_user(self, email, alias, password=None):
        if not email:
            raise ValueError("El usuario debe tener un correo electrónico")
        
        user = self.model(
            email=self.normalize_email(email),
            alias=alias
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, alias, password):
        user = self.create_user(
            email=email,
            alias=alias,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

# Modelo de usuario personalizado
class CustomUser(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    alias = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['alias']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

