from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

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


# Obtener el modelo de usuario personalizado
User = get_user_model()

class Ramo(models.Model):
    nombre = models.CharField(max_length=255)
    dificultad = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario

    def __str__(self):
        return self.nombre

class HorarioRamo(models.Model):
    ramo = models.ForeignKey(Ramo, related_name='horarios', on_delete=models.CASCADE)
    dia = models.CharField(max_length=10)
    hora_inicio = models.TimeField()
    hora_termino = models.TimeField()

    def __str__(self):
        return f"{self.dia} {self.hora_inicio}-{self.hora_termino}"

class ActividadExtracurricular(models.Model):
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=[('fijo', 'Fijo'), ('semanal', 'Semanal')])
    horas_semanales = models.IntegerField(null=True, blank=True)  # Solo si es semanal
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario

    def __str__(self):
        return self.nombre

class HorarioActividad(models.Model):
    actividad = models.ForeignKey(ActividadExtracurricular, related_name='horarios', on_delete=models.CASCADE)
    dia = models.CharField(max_length=10)
    hora_inicio = models.TimeField()
    hora_termino = models.TimeField()

    def __str__(self):
        return f"{self.dia} {self.hora_inicio}-{self.hora_termino}"
    
from django.conf import settings  # Importa settings para obtener el modelo de usuario configurado
from django.db import models


class Preferencia(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Relación con modelo de usuario personalizado
    horario_estudio = models.CharField(max_length=10, choices=[('mañana', 'Mañana'), ('tarde', 'Tarde'), ('noche', 'Noche')])
    tiempo_llegada_uni = models.IntegerField(default=0)  # Tiempo en minutos
    tiempo_preparacion = models.IntegerField(default=0)  # Tiempo en minutos desde que despierta
    lugar_estudio = models.CharField(max_length=50, blank=True)  # Lugar donde le gusta estudiar
    tiempo_antes_dormir = models.IntegerField(default=0)  # Tiempo en minutos antes de dormir para terminar actividades
    preferencias_personalizadas = models.TextField(blank=True, null=True)  # Texto con múltiples preferencias personalizadas

    def __str__(self):
        return f"Preferencias de {self.usuario.alias}"

