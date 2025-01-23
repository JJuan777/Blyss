from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, correo, nombre, apellidos, password=None, **extra_fields):
        """
        Crea y retorna un usuario con el correo y contraseña proporcionados.
        """
        if not correo:
            raise ValueError("El usuario debe tener un correo electrónico")
        correo = self.normalize_email(correo)
        usuario = self.model(correo=correo, Nombre=nombre, Apellidos=apellidos, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, correo, nombre, apellidos, password=None, **extra_fields):
        """
        Crea y retorna un superusuario con el correo y contraseña proporcionados.
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        return self.create_user(correo, nombre, apellidos, password, **extra_fields)

class Usuarios(AbstractBaseUser):
    IdUsuario = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=100)
    Apellidos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    Telefono = models.CharField(max_length=20, blank=True, null=True)
    Pais = models.CharField(max_length=50)
    FechaDeNacimiento = models.DateField(null=True, blank=True)
    Genero = models.CharField(max_length=50, blank=True, null=True)
    ImgUsuario = models.BinaryField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['Nombre', 'Apellidos']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.Nombre} {self.Apellidos} ({self.correo})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
