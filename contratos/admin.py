from django.contrib import admin
from .models import Contrato, FirmaDigital


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['numero_contrato', 'inmueble', 'inquilino', 'estado', 
                   'fecha_inicio', 'fecha_fin', 'valor_arriendo']
    list_filter = ['estado', 'fecha_inicio', 'fecha_fin']
    search_fields = ['numero_contrato', 'inmueble__titulo', 'inquilino__username']
    readonly_fields = ['numero_contrato', 'fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_contrato', 'inmueble', 'inquilino', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin', 'fecha_creacion', 'fecha_actualizacion')
        }),
        ('Condiciones Económicas', {
            'fields': ('valor_arriendo', 'valor_administracion', 'valor_deposito', 'dia_pago')
        }),
        ('Firmas Digitales', {
            'fields': (
                'firma_propietario', 'fecha_firma_propietario',
                'firma_inquilino', 'fecha_firma_inquilino'
            )
        }),
        ('Términos', {
            'fields': ('terminos_condiciones', 'clausulas_especiales', 'documento_contrato')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(FirmaDigital)
class FirmaDigitalAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_firma', 'ip_address']
    list_filter = ['fecha_firma']
    search_fields = ['usuario__username', 'ip_address']
    readonly_fields = ['fecha_firma']
