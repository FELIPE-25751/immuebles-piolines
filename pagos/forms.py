from django import forms
from .models import Pago, RegistroPago


class RegistrarPagoForm(forms.ModelForm):
    """Formulario para registrar un pago"""
    
    class Meta:
        model = RegistroPago
        fields = ['monto', 'metodo_pago', 'referencia', 'comprobante', 'notas']
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'placeholder': 'Monto pagado'
            }),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de referencia'
            }),
            'comprobante': forms.FileInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            }),
        }


class FiltrarPagosForm(forms.Form):
    """Formulario para filtrar pagos"""
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Pago.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Desde'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Hasta'
        })
    )
