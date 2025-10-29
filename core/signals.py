from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, PerfilUsuario


@receiver(post_save, sender=Usuario)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crear perfil automáticamente cuando se crea un usuario"""
    if created:
        PerfilUsuario.objects.create(usuario=instance)
        instance.save_to_firebase()


@receiver(post_save, sender=Usuario)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guardar perfil cuando se actualiza el usuario"""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
