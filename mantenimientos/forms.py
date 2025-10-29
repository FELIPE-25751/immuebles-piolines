from django import forms
from .models import Mantenimiento, SeguimientoMantenimiento
from inmuebles.models import Inmueble


class MantenimientoForm(forms.ModelForm):
    """Formulario para solicitar mantenimiento"""
    
    class Meta:
        model = Mantenimiento
        fields = ['inmueble', 'titulo', 'descripcion', 'tipo', 'prioridad', 
                 'ubicacion_especifica', 'imagen']
        widgets = {
            'inmueble': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion_especifica': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        if usuario:
            if usuario.tipo_usuario == 'inquilino':
                # Filtrar solo inmuebles donde el usuario es inquilino activo
                from contratos.models import Contrato
                contratos_activos = Contrato.objects.filter(
                    inquilino=usuario,
                    estado='activo'
                )
                inmuebles_ids = [c.inmueble.id for c in contratos_activos]
                self.fields['inmueble'].queryset = Inmueble.objects.filter(
                    id__in=inmuebles_ids
                )
            elif usuario.tipo_usuario == 'propietario':
                # Propietarios pueden ver todos sus inmuebles
                self.fields['inmueble'].queryset = Inmueble.objects.filter(
                    propietario=usuario
                )


class GestionarMantenimientoForm(forms.ModelForm):
    """Formulario para gestionar mantenimiento (propietarios)"""
    
    class Meta:
        model = Mantenimiento
        fields = ['estado', 'fecha_estimada', 'costo_estimado', 'costo_final', 
                 'responsable_costo', 'notas_propietario', 'solucion_aplicada']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_estimada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'costo_estimado': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'costo_final': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'responsable_costo': forms.Select(attrs={'class': 'form-control'}),
            'notas_propietario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'solucion_aplicada': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SeguimientoForm(forms.ModelForm):
    """Formulario para agregar seguimiento"""
    
    class Meta:
        model = SeguimientoMantenimiento
        fields = ['comentario', 'archivo_adjunto']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe un comentario...'
            }),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FiltrarMantenimientosForm(forms.Form):
    """Formulario para filtrar mantenimientos"""
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Mantenimiento.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + Mantenimiento.TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    prioridad = forms.ChoiceField(
        choices=[('', 'Todas las prioridades')] + Mantenimiento.PRIORIDAD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
