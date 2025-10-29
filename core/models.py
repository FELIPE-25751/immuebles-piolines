from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
from django.conf import settings
import os

# Inicializar Firebase
if not firebase_admin._apps:
    cred_path = os.path.join(settings.BASE_DIR, settings.FIREBASE_CREDENTIALS_PATH)
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)


class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado con roles
    """
    TIPO_USUARIO = [
        ('propietario', 'Propietario'),
        ('inquilino', 'Inquilino'),
    ]
    
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO)
    telefono = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    cedula = models.CharField(max_length=20, unique=True)
    direccion = models.TextField(blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    firebase_uid = models.CharField(max_length=255, blank=True, unique=True, null=True)
    
    # Campos adicionales
    ciudad = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, default='Colombia')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_tipo_usuario_display()})"
    
    def get_inmuebles(self):
        """Retorna los inmuebles según el tipo de usuario"""
        if self.tipo_usuario == 'propietario':
            return self.inmuebles_propietario.all()
        else:
            # Retorna inmuebles donde el usuario es inquilino activo
            from contratos.models import Contrato
            contratos_activos = Contrato.objects.filter(
                inquilino=self,
                estado='activo'
            )
            return [c.inmueble for c in contratos_activos]
    
    def save_to_firebase(self):
        """Guarda el usuario en Firebase"""
        try:
            db = firestore.client()
            user_ref = db.collection('usuarios').document(str(self.id))
            user_ref.set({
                'username': self.username,
                'email': self.email,
                'tipo_usuario': self.tipo_usuario,
                'telefono': self.telefono,
                'cedula': self.cedula,
                'nombre_completo': self.get_full_name(),
                'fecha_registro': self.date_joined,
                'firebase_uid': self.firebase_uid or ''
            })
            return True
        except Exception as e:
            print(f"Error al guardar en Firebase: {e}")
            return False


class PerfilUsuario(models.Model):
    """
    Información adicional del perfil de usuario
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    biografia = models.TextField(blank=True)
    calificacion_promedio = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    numero_calificaciones = models.IntegerField(default=0)
    verificado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
