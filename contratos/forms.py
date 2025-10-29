from django import forms
from .models import Contrato
from inmuebles.models import Inmueble
from core.models import Usuario


class ContratoForm(forms.ModelForm):
    """Formulario para crear y editar contratos"""
    
    class Meta:
        model = Contrato
        fields = [
            'inmueble', 'inquilino', 'fecha_inicio', 'fecha_fin',
            'valor_arriendo', 'valor_administracion', 'valor_deposito',
            'dia_pago', 'terminos_condiciones', 'clausulas_especiales'
        ]
        widgets = {
            'inmueble': forms.Select(attrs={'class': 'form-control'}),
            'inquilino': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_arriendo': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'valor_administracion': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'valor_deposito': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'dia_pago': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '31'}),
            'terminos_condiciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'clausulas_especiales': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        propietario = kwargs.pop('propietario', None)
        super().__init__(*args, **kwargs)
        
        if propietario:
            # Filtrar solo inmuebles del propietario que estén disponibles
            self.fields['inmueble'].queryset = Inmueble.objects.filter(
                propietario=propietario,
                estado='disponible'
            )
        
        # Filtrar solo usuarios tipo inquilino
        self.fields['inquilino'].queryset = Usuario.objects.filter(tipo_usuario='inquilino')


class FirmaContratoForm(forms.Form):
    """Formulario para firma digital de contratos"""
    
    firma = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    acepto_terminos = forms.BooleanField(
        required=True,
        label='Acepto los términos y condiciones del contrato',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class BusquedaContratoForm(forms.Form):
    """Formulario para búsqueda de contratos"""
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Contrato.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
