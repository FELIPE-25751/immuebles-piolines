from django.contrib import admin
from .models import Notificacion, ConfiguracionNotificaciones


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'tipo', 'prioridad', 'leida', 'fecha_creacion']
    list_filter = ['tipo', 'prioridad', 'leida', 'fecha_creacion']
    search_fields = ['titulo', 'mensaje', 'usuario__username']
    readonly_fields = ['fecha_creacion', 'fecha_lectura']
    
    fieldsets = (
        ('Destinatario', {
            'fields': ('usuario',)
        }),
        ('Contenido', {
            'fields': ('titulo', 'mensaje', 'tipo', 'prioridad', 'enlace')
        }),
        ('Estado', {
            'fields': ('leida', 'fecha_lectura', 'fecha_creacion')
        }),
    )


@admin.register(ConfiguracionNotificaciones)
class ConfiguracionNotificacionesAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'notif_contratos', 'notif_pagos', 'notif_mantenimientos']
    search_fields = ['usuario__username']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Notificaciones en Sistema', {
            'fields': ('notif_inmuebles', 'notif_contratos', 'notif_pagos', 
                      'notif_mantenimientos', 'notif_mensajes')
        }),
        ('Notificaciones por Email', {
            'fields': ('email_inmuebles', 'email_contratos', 'email_pagos', 
                      'email_mantenimientos')
        }),
    )
