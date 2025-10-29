from django.contrib import admin
from .models import Inmueble, ImagenInmueble, CaracteristicaAdicional


class ImagenInmuebleInline(admin.TabularInline):
    model = ImagenInmueble
    extra = 1


class CaracteristicaAdicionalInline(admin.TabularInline):
    model = CaracteristicaAdicional
    extra = 1


@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'propietario', 'categoria', 'estado', 'precio_arriendo', 
                   'ciudad', 'fecha_registro']
    list_filter = ['categoria', 'estado', 'ciudad', 'amoblado', 'mascotas_permitidas']
    search_fields = ['titulo', 'descripcion', 'direccion', 'ciudad', 'barrio']
    inlines = [ImagenInmuebleInline, CaracteristicaAdicionalInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('propietario', 'titulo', 'descripcion', 'categoria', 'estado')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad', 'barrio', 'codigo_postal')
        }),
        ('Características', {
            'fields': ('area', 'habitaciones', 'banos', 'parqueaderos', 'piso')
        }),
        ('Información Económica', {
            'fields': ('precio_arriendo', 'precio_administracion', 'deposito_seguridad')
        }),
        ('Características Adicionales', {
            'fields': ('amoblado', 'mascotas_permitidas')
        }),
        ('Servicios', {
            'fields': ('agua_incluida', 'luz_incluida', 'gas_incluida', 'internet_incluido')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(ImagenInmueble)
class ImagenInmuebleAdmin(admin.ModelAdmin):
    list_display = ['inmueble', 'descripcion', 'principal', 'orden', 'fecha_subida']
    list_filter = ['principal', 'fecha_subida']
    search_fields = ['inmueble__titulo', 'descripcion']
