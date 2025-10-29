from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Notificacion, ConfiguracionNotificaciones


@login_required
def listar_notificaciones(request):
    """Vista para listar todas las notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    
    # Filtrar por estado si se proporciona
    estado = request.GET.get('estado')
    if estado == 'no_leidas':
        notificaciones = notificaciones.filter(leida=False)
    elif estado == 'leidas':
        notificaciones = notificaciones.filter(leida=True)
    
    # Filtrar por tipo si se proporciona
    tipo = request.GET.get('tipo')
    if tipo:
        notificaciones = notificaciones.filter(tipo=tipo)
    
    paginator = Paginator(notificaciones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contar no leídas
    no_leidas = Notificacion.objects.filter(usuario=request.user, leida=False).count()
    
    context = {
        'notificaciones': page_obj,
        'no_leidas': no_leidas,
    }
    return render(request, 'notificaciones/listar.html', context)


@login_required
def marcar_como_leida(request, notificacion_id):
    """Vista para marcar una notificación como leída"""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.marcar_como_leida()
    
    # Si hay un enlace, redirigir allí
    if notificacion.enlace:
        return redirect(notificacion.enlace)
    
    return redirect('notificaciones:listar')


@login_required
def marcar_todas_leidas(request):
    """Vista para marcar todas las notificaciones como leídas"""
    if request.method == 'POST':
        Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        messages.success(request, 'Todas las notificaciones han sido marcadas como leídas.')
    
    return redirect('notificaciones:listar')


@login_required
def eliminar_notificacion(request, notificacion_id):
    """Vista para eliminar una notificación"""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    
    if request.method == 'POST':
        notificacion.delete()
        messages.success(request, 'Notificación eliminada exitosamente.')
    
    return redirect('notificaciones:listar')


@login_required
def configuracion(request):
    """Vista para configurar las notificaciones"""
    config, created = ConfiguracionNotificaciones.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        # Actualizar configuración
        config.notif_inmuebles = 'notif_inmuebles' in request.POST
        config.notif_contratos = 'notif_contratos' in request.POST
        config.notif_pagos = 'notif_pagos' in request.POST
        config.notif_mantenimientos = 'notif_mantenimientos' in request.POST
        config.notif_mensajes = 'notif_mensajes' in request.POST
        
        config.email_inmuebles = 'email_inmuebles' in request.POST
        config.email_contratos = 'email_contratos' in request.POST
        config.email_pagos = 'email_pagos' in request.POST
        config.email_mantenimientos = 'email_mantenimientos' in request.POST
        
        config.save()
        messages.success(request, 'Configuración actualizada exitosamente.')
        return redirect('notificaciones:configuracion')
    
    return render(request, 'notificaciones/configuracion.html', {'config': config})


@login_required
def obtener_no_leidas(request):
    """API endpoint para obtener el número de notificaciones no leídas"""
    no_leidas = Notificacion.objects.filter(usuario=request.user, leida=False).count()
    
    # Obtener las últimas 5 notificaciones no leídas
    ultimas = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    )[:5]
    
    notificaciones_data = [{
        'id': n.id,
        'titulo': n.titulo,
        'mensaje': n.mensaje,
        'tipo': n.tipo,
        'enlace': n.enlace,
        'fecha': n.fecha_creacion.isoformat()
    } for n in ultimas]
    
    return JsonResponse({
        'no_leidas': no_leidas,
        'notificaciones': notificaciones_data
    })
