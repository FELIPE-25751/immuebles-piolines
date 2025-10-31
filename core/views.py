from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from datetime import datetime, timedelta
from .forms import RegistroForm, LoginForm, PerfilForm
from .models import Usuario
from inmuebles.models import Inmueble
from contratos.models import Contrato
from pagos.models import Pago
from mantenimientos.models import Mantenimiento
from notificaciones.models import Notificacion
from django.utils import timezone
# Vista de reportes generales para propietario
@login_required
def reportes_generales(request):
    usuario = request.user
    if usuario.tipo_usuario != 'propietario':
        messages.error(request, 'Solo los propietarios pueden acceder a los reportes generales.')
        return redirect('core:dashboard')

    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    inmueble_filtro = request.GET.get('inmueble')

    inmuebles = Inmueble.objects.filter(propietario=usuario)
    pagos = Pago.objects.filter(contrato__inmueble__propietario=usuario)
    mantenimientos = Mantenimiento.objects.filter(inmueble__propietario=usuario)
    contratos = Contrato.objects.filter(inmueble__propietario=usuario)

    if inmueble_filtro:
        pagos = pagos.filter(contrato__inmueble_id=inmueble_filtro)
        mantenimientos = mantenimientos.filter(inmueble_id=inmueble_filtro)
        contratos = contratos.filter(inmueble_id=inmueble_filtro)

    if fecha_desde:
        pagos = pagos.filter(fecha_pago__gte=fecha_desde)
        mantenimientos = mantenimientos.filter(fecha_solicitud__gte=fecha_desde)
        contratos = contratos.filter(fecha_inicio__gte=fecha_desde)
    if fecha_hasta:
        pagos = pagos.filter(fecha_pago__lte=fecha_hasta)
        mantenimientos = mantenimientos.filter(fecha_solicitud__lte=fecha_hasta)
        contratos = contratos.filter(fecha_fin__lte=fecha_hasta)

    # KPIs
        total_pagos_recibidos = pagos.filter(estado='pagado').aggregate(total=Sum('monto'))['total'] or 0
        total_pagos_pendientes = pagos.filter(estado='pendiente').aggregate(total=Sum('monto'))['total'] or 0
    mantenimientos_activos = mantenimientos.exclude(estado__in=['completado','cancelado','rechazado']).count()
    contratos_vigentes = contratos.filter(estado='activo').count()

    context = {
        'inmuebles': inmuebles,
        'pagos': pagos.order_by('-fecha_pago')[:50],
        'mantenimientos': mantenimientos.order_by('-fecha_solicitud')[:50],
        'contratos': contratos.order_by('-fecha_inicio')[:50],
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'inmueble_filtro': inmueble_filtro,
        'total_pagos_recibidos': total_pagos_recibidos,
        'total_pagos_pendientes': total_pagos_pendientes,
        'mantenimientos_activos': mantenimientos_activos,
        'contratos_vigentes': contratos_vigentes,
    }
    return render(request, 'core/reportes_generales.html', context)

def index(request):
    """Vista de página principal"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/index.html')


def registro(request):
    """Vista de registro de usuarios"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'¡Bienvenido {usuario.first_name}! Tu cuenta ha sido creada exitosamente.')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    
    return render(request, 'core/registro.html', {'form': form})


def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {user.first_name}!')
                return redirect('core:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('core:login')


@login_required
def dashboard(request):
    """Dashboard principal con estadísticas"""
    user = request.user
    context = {
        'usuario': user,
    }
    
    if user.tipo_usuario == 'propietario':
        # Estadísticas para propietarios
        inmuebles = Inmueble.objects.filter(propietario=user)
        contratos = Contrato.objects.filter(inmueble__propietario=user)
        
        context.update({
            'total_inmuebles': inmuebles.count(),
            'inmuebles_disponibles': inmuebles.filter(estado='disponible').count(),
            'inmuebles_arrendados': inmuebles.filter(estado='arrendado').count(),
            'total_contratos': contratos.count(),
            'contratos_activos': contratos.filter(estado='activo').count(),
            'contratos_vencidos': contratos.filter(estado='vencido').count(),
            'pagos_pendientes': Pago.objects.filter(
                contrato__inmueble__propietario=user,
                estado='pendiente'
            ).count(),
            'mantenimientos_activos': Mantenimiento.objects.filter(
                inmueble__propietario=user,
                estado='activo'
            ).count(),
            'inmuebles_recientes': inmuebles.order_by('-fecha_registro')[:5],
            'ultimos_pagos': Pago.objects.filter(
                contrato__inmueble__propietario=user
            ).order_by('-fecha_pago')[:5],
        })
        
    else:  # inquilino
        # Estadísticas para inquilinos
        contratos = Contrato.objects.filter(inquilino=user)
        
        context.update({
            'total_contratos': contratos.count(),
            'contratos_activos': contratos.filter(estado='activo').count(),
            'inmuebles_actuales': [c.inmueble for c in contratos.filter(estado='activo')],
            'pagos_pendientes': Pago.objects.filter(
                contrato__inquilino=user,
                estado='pendiente'
            ).count(),
            'pagos_vencidos': Pago.objects.filter(
                contrato__inquilino=user,
                estado='vencido'
            ).count(),
            'mantenimientos_activos': Mantenimiento.objects.filter(
                inmueble__contratos__inquilino=user,
                estado='activo'
            ).count(),
            'ultimos_pagos': Pago.objects.filter(
                contrato__inquilino=user
            ).order_by('-fecha_pago')[:5],
        })
    
    # Notificaciones recientes para todos
    context['notificaciones'] = Notificacion.objects.filter(
        usuario=user,
        leida=False
    ).order_by('-fecha_creacion')[:5]
    
    return render(request, 'core/dashboard.html', context)


@login_required
def perfil(request):
    """Vista de perfil de usuario"""
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('core:perfil')
    else:
        form = PerfilForm(instance=request.user)
    
    return render(request, 'core/perfil.html', {'form': form})


@login_required
def perfil_usuario(request, user_id):
    """Vista de perfil público de otro usuario"""
    usuario = Usuario.objects.get(id=user_id)
    
    context = {
        'usuario_perfil': usuario,
    }
    
    if usuario.tipo_usuario == 'propietario':
        context['inmuebles'] = Inmueble.objects.filter(
            propietario=usuario,
            estado='disponible'
        )[:6]
    
    return render(request, 'core/perfil_publico.html', context)
