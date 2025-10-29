from django.contrib import admin
from .models import Pago, RegistroPago


class RegistroPagoInline(admin.TabularInline):
    model = RegistroPago
    extra = 0
    readonly_fields = ['fecha_registro']


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['numero_pago', 'contrato', 'concepto', 'monto', 
                   'fecha_vencimiento', 'estado']
    list_filter = ['estado', 'metodo_pago', 'fecha_vencimiento']
    search_fields = ['numero_pago', 'concepto', 'contrato__numero_contrato']
    readonly_fields = ['numero_pago', 'fecha_creacion']
    inlines = [RegistroPagoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_pago', 'contrato', 'concepto', 'descripcion')
        }),
        ('Montos', {
            'fields': ('monto', 'monto_pagado', 'mora')
        }),
        ('Fechas', {
            'fields': ('periodo_inicio', 'periodo_fin', 'fecha_vencimiento', 
                      'fecha_pago', 'fecha_creacion')
        }),
        ('Pago', {
            'fields': ('estado', 'metodo_pago', 'referencia_pago', 'comprobante')
        }),
        ('Cuenta de Cobro', {
            'fields': ('cuenta_cobro_generada', 'fecha_generacion_cuenta', 
                      'archivo_cuenta_cobro')
        }),
    )


@admin.register(RegistroPago)
class RegistroPagoAdmin(admin.ModelAdmin):
    list_display = ['pago', 'monto', 'metodo_pago', 'fecha_registro', 'registrado_por']
    list_filter = ['metodo_pago', 'fecha_registro']
    search_fields = ['pago__numero_pago', 'referencia']
    readonly_fields = ['fecha_registro']
