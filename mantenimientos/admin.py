from django.contrib import admin
from .models import Mantenimiento, SeguimientoMantenimiento


class SeguimientoMantenimientoInline(admin.TabularInline):
    model = SeguimientoMantenimiento
    extra = 0
    readonly_fields = ['fecha']


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ['numero_ticket', 'titulo', 'inmueble', 'solicitante', 
                   'tipo', 'prioridad', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'tipo', 'prioridad', 'fecha_solicitud']
    search_fields = ['numero_ticket', 'titulo', 'inmueble__titulo']
    readonly_fields = ['numero_ticket', 'fecha_solicitud']
    inlines = [SeguimientoMantenimientoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_ticket', 'inmueble', 'solicitante', 'asignado_a')
        }),
        ('Detalles del Mantenimiento', {
            'fields': ('titulo', 'descripcion', 'tipo', 'prioridad', 'estado', 
                      'ubicacion_especifica')
        }),
        ('Fechas', {
            'fields': ('fecha_solicitud', 'fecha_revision', 'fecha_inicio', 
                      'fecha_completado', 'fecha_estimada')
        }),
        ('Costos', {
            'fields': ('costo_estimado', 'costo_final', 'responsable_costo')
        }),
        ('Notas', {
            'fields': ('notas_propietario', 'solucion_aplicada')
        }),
        ('Archivos', {
            'fields': ('imagen',)
        }),
    )


@admin.register(SeguimientoMantenimiento)
class SeguimientoMantenimientoAdmin(admin.ModelAdmin):
    list_display = ['mantenimiento', 'usuario', 'fecha']
    list_filter = ['fecha']
    search_fields = ['mantenimiento__numero_ticket', 'usuario__username', 'comentario']
    readonly_fields = ['fecha']
