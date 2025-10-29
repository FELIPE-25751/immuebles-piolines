from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilUsuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'tipo_usuario', 'cedula', 'is_staff']
    list_filter = ['tipo_usuario', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'cedula', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('tipo_usuario', 'cedula', 'telefono', 'direccion', 
                      'fecha_nacimiento', 'foto_perfil', 'ciudad', 'pais', 'firebase_uid')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('tipo_usuario', 'cedula', 'email')
        }),
    )


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'calificacion_promedio', 'verificado', 'activo']
    list_filter = ['verificado', 'activo']
    search_fields = ['usuario__username', 'usuario__email']
