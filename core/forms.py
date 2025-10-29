from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario
from django.core.exceptions import ValidationError


class RegistroForm(UserCreationForm):
    """Formulario de registro de usuarios"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )
    
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    cedula = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cédula'
        })
    )
    
    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono'
        })
    )
    
    tipo_usuario = forms.ChoiceField(
        choices=Usuario.TIPO_USUARIO,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'cedula', 
                 'telefono', 'tipo_usuario', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )


class PerfilForm(forms.ModelForm):
    """Formulario de edición de perfil"""
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'direccion', 
                 'ciudad', 'fecha_nacimiento', 'foto_perfil']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
