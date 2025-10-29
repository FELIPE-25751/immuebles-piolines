from django import forms
from .models import Inmueble, ImagenInmueble, CaracteristicaAdicional


class InmuebleForm(forms.ModelForm):
    """Formulario para crear y editar inmuebles"""
    
    class Meta:
        model = Inmueble
        fields = [
            'titulo', 'descripcion', 'categoria', 'estado',
            'direccion', 'ciudad', 'barrio', 'codigo_postal',
            'area', 'habitaciones', 'banos', 'parqueaderos', 'piso',
            'precio_arriendo', 'precio_administracion', 'deposito_seguridad',
            'amoblado', 'mascotas_permitidas',
            'agua_incluida', 'luz_incluida', 'gas_incluida', 'internet_incluido'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'habitaciones': forms.NumberInput(attrs={'class': 'form-control'}),
            'banos': forms.NumberInput(attrs={'class': 'form-control'}),
            'parqueaderos': forms.NumberInput(attrs={'class': 'form-control'}),
            'piso': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_arriendo': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'precio_administracion': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'deposito_seguridad': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'amoblado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mascotas_permitidas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'agua_incluida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'luz_incluida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gas_incluida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'internet_incluido': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ImagenInmuebleForm(forms.ModelForm):
    """Formulario para subir imágenes de inmuebles"""
    
    class Meta:
        model = ImagenInmueble
        fields = ['imagen', 'descripcion', 'principal']
        widgets = {
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BusquedaInmuebleForm(forms.Form):
    """Formulario para búsqueda y filtrado de inmuebles"""
    
    categoria = forms.ChoiceField(
        choices=[('', 'Todas las categorías')] + Inmueble.CATEGORIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    ciudad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ciudad'
        })
    )
    
    precio_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio mínimo',
            'step': '100000'
        })
    )
    
    precio_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio máximo',
            'step': '100000'
        })
    )
    
    habitaciones = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Habitaciones'
        })
    )
    
    banos = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Baños'
        })
    )
    
    amoblado = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    mascotas_permitidas = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
