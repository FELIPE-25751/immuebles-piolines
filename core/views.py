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
from django.conf import settings
import requests
import random
# Protección contra fuerza bruta (import seguro)
try:
    from ratelimit.decorators import ratelimit  # type: ignore[reportMissingImports]
except ImportError:  # Si no está instalado en el entorno, usar un decorador no-op para no romper producción
    from typing import Any, Callable

    def ratelimit(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def wrapper(view_func: Callable[..., Any]) -> Callable[..., Any]:
            return view_func
        return wrapper

# Utilidades simples de CAPTCHA (fallback cuando no hay Turnstile)
def _prepare_simple_captcha(request):
    """Genera y guarda en sesión un desafío aritmético simple."""
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    request.session['captcha_sum'] = a + b
    request.session['captcha_ts'] = int(timezone.now().timestamp())
    return {'captcha_a': a, 'captcha_b': b}

def _validate_simple_captcha(request):
    """Valida el CAPTCHA simple basado en sesión. Devuelve (ok, mensaje_error)."""
    # Honeypot: bots suelen completar campos ocultos
    if request.POST.get('website'):
        return False, 'Detección de bot (honeypot).'
    try:
        answer = int(request.POST.get('captcha_answer', '').strip())
    except Exception:
        return False, 'Resuelve la pregunta de verificación.'

    expected = request.session.get('captcha_sum')
    ts = request.session.get('captcha_ts')
    if expected is None or ts is None:
        return False, 'Vuelve a intentar la verificación.'
    # Expira en 3 minutos
    now_ts = int(timezone.now().timestamp())
    if now_ts - int(ts) > 180:
        return False, 'La verificación expiró. Intenta nuevamente.'
    if answer != int(expected):
        return False, 'Respuesta incorrecta de verificación.'
    return True, ''
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


@ratelimit(key='ip', rate='3/m', block=True)
@ratelimit(key='post:username', rate='3/m', block=True)
def registro(request):
    """Vista de registro de usuarios"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        # Verificar Turnstile si está configurado
        if settings.TURNSTILE_SECRET_KEY:
            token = request.POST.get('cf-turnstile-response')
            if not token:
                messages.error(request, 'Por favor completa la verificación de seguridad (CAPTCHA).')
                form = RegistroForm(request.POST)
                ctx = {'form': form, 'turnstile_site_key': settings.TURNSTILE_SITE_KEY}
                return render(request, 'core/registro.html', ctx)
            try:
                resp = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data={
                    'secret': settings.TURNSTILE_SECRET_KEY,
                    'response': token,
                    'remoteip': request.META.get('REMOTE_ADDR')
                }, timeout=5)
                ok = resp.json().get('success', False)
            except Exception:
                ok = False
            if not ok:
                messages.error(request, 'No pudimos verificar que eres humano. Intenta de nuevo.')
                form = RegistroForm(request.POST)
                ctx = {'form': form, 'turnstile_site_key': settings.TURNSTILE_SITE_KEY}
                return render(request, 'core/registro.html', ctx)
        else:
            # Fallback CAPTCHA simple sin claves/env vars
            ok, err = _validate_simple_captcha(request)
            if not ok:
                messages.error(request, err)
                form = RegistroForm(request.POST)
                # Generar nuevo desafío
                ctx = {'form': form, 'turnstile_site_key': '', **_prepare_simple_captcha(request)}
                return render(request, 'core/registro.html', ctx)
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
        # Preparar desafío solo si no hay Turnstile
        extra = _prepare_simple_captcha(request) if not settings.TURNSTILE_SECRET_KEY else {}
    
    return render(request, 'core/registro.html', {'form': form, 'turnstile_site_key': settings.TURNSTILE_SITE_KEY, **extra})


@ratelimit(key='ip', rate='5/m', block=True)
@ratelimit(key='post:username', rate='5/m', block=True)
def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        # Verificar Turnstile si está configurado
        if settings.TURNSTILE_SECRET_KEY:
            token = request.POST.get('cf-turnstile-response')
            if not token:
                messages.error(request, 'Por favor completa la verificación de seguridad (CAPTCHA).')
                form = LoginForm(request, data=request.POST)
                ctx = {'form': form, 'turnstile_site_key': settings.TURNSTILE_SITE_KEY}
                return render(request, 'core/login.html', ctx)
            try:
                resp = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data={
                    'secret': settings.TURNSTILE_SECRET_KEY,
                    'response': token,
                    'remoteip': request.META.get('REMOTE_ADDR')
                }, timeout=5)
                ok = resp.json().get('success', False)
            except Exception:
                ok = False
            if not ok:
                messages.error(request, 'No pudimos verificar que eres humano. Intenta de nuevo.')
                form = LoginForm(request, data=request.POST)
                ctx = {'form': form, 'turnstile_site_key': settings.TURNSTILE_SITE_KEY}
                return render(request, 'core/login.html', ctx)
        else:
            # Fallback CAPTCHA simple sin claves/env vars
            ok, err = _validate_simple_captcha(request)
            if not ok:
                messages.error(request, err)
                form = LoginForm(request, data=request.POST)
                ctx = {'form': form, 'turnstile_site_key': ''}
                ctx.update(_prepare_simple_captcha(request))
                return render(request, 'core/login.html', ctx)
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
        # Preparar desafío solo si no hay Turnstile
        extra = _prepare_simple_captcha(request) if not settings.TURNSTILE_SECRET_KEY else {}
    
    return render(request, 'core/login.html', {'form': form, 'turnstile_site_key': settings.TURNSTILE_SITE_KEY, **extra})


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
