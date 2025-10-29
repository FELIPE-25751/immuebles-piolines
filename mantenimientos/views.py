from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Mantenimiento, SeguimientoMantenimiento
from .forms import MantenimientoForm, GestionarMantenimientoForm, SeguimientoForm, FiltrarMantenimientosForm
from notificaciones.models import Notificacion


@login_required
def listar_mantenimientos(request):
    """Vista para listar mantenimientos según el tipo de usuario"""
    user = request.user
    form = FiltrarMantenimientosForm(request.GET)
    
    if user.tipo_usuario == 'propietario':
        mantenimientos = Mantenimiento.objects.filter(inmueble__propietario=user)
    else:  # inquilino
        mantenimientos = Mantenimiento.objects.filter(solicitante=user)
    
    # Aplicar filtros
    if form.is_valid():
        estado = form.cleaned_data.get('estado')
        tipo = form.cleaned_data.get('tipo')
        prioridad = form.cleaned_data.get('prioridad')
        
        if estado:
            mantenimientos = mantenimientos.filter(estado=estado)
        if tipo:
            mantenimientos = mantenimientos.filter(tipo=tipo)
        if prioridad:
            mantenimientos = mantenimientos.filter(prioridad=prioridad)
    
    paginator = Paginator(mantenimientos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'mantenimientos': page_obj,
        'form': form,
    }
    return render(request, 'mantenimientos/listar.html', context)


@login_required
def detalle_mantenimiento(request, mantenimiento_id):
    """Vista para ver detalles de un mantenimiento"""
    mantenimiento = get_object_or_404(Mantenimiento, id=mantenimiento_id)
    
    # Verificar permisos
    if request.user.tipo_usuario == 'propietario':
        if mantenimiento.inmueble.propietario != request.user:
            messages.error(request, 'No tienes permiso para ver este mantenimiento.')
            return redirect('mantenimientos:listar')
    else:
        if mantenimiento.solicitante != request.user:
            messages.error(request, 'No tienes permiso para ver este mantenimiento.')
            return redirect('mantenimientos:listar')
    
    seguimientos = mantenimiento.seguimientos.all()
    
    context = {
        'mantenimiento': mantenimiento,
        'seguimientos': seguimientos,
    }
    return render(request, 'mantenimientos/detalle.html', context)


@login_required
def solicitar_mantenimiento(request):
    """Vista para solicitar un nuevo mantenimiento"""
    if request.method == 'POST':
        form = MantenimientoForm(request.POST, request.FILES, usuario=request.user)
        if form.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.solicitante = request.user
            mantenimiento.estado = 'pendiente'
            mantenimiento.save()
            mantenimiento.save_to_firebase()
            
            # Notificar al propietario
            Notificacion.objects.create(
                usuario=mantenimiento.inmueble.propietario,
                titulo='Nueva Solicitud de Mantenimiento',
                mensaje=f'Nueva solicitud: {mantenimiento.titulo} en {mantenimiento.inmueble.titulo}',
                tipo='mantenimiento',
                enlace=f'/mantenimientos/{mantenimiento.id}/'
            )
            
            messages.success(request, 'Solicitud de mantenimiento enviada exitosamente.')
            return redirect('mantenimientos:detalle', mantenimiento_id=mantenimiento.id)
    else:
        form = MantenimientoForm(usuario=request.user)
    
    return render(request, 'mantenimientos/form.html', {
        'form': form,
        'titulo': 'Solicitar Mantenimiento'
    })


@login_required
def gestionar_mantenimiento(request, mantenimiento_id):
    """Vista para gestionar un mantenimiento (solo propietarios)"""
    mantenimiento = get_object_or_404(Mantenimiento, id=mantenimiento_id)
    
    # Solo el propietario puede gestionar
    if mantenimiento.inmueble.propietario != request.user:
        messages.error(request, 'No tienes permiso para gestionar este mantenimiento.')
        return redirect('mantenimientos:detalle', mantenimiento_id=mantenimiento.id)
    
    if request.method == 'POST':
        form = GestionarMantenimientoForm(request.POST, instance=mantenimiento)
        if form.is_valid():
            mantenimiento_actualizado = form.save()
            
            # Actualizar fechas según el estado
            if mantenimiento_actualizado.estado == 'en_revision' and not mantenimiento.fecha_revision:
                mantenimiento_actualizado.fecha_revision = timezone.now()
            elif mantenimiento_actualizado.estado == 'en_proceso' and not mantenimiento.fecha_inicio:
                mantenimiento_actualizado.fecha_inicio = timezone.now()
            elif mantenimiento_actualizado.estado == 'completado' and not mantenimiento.fecha_completado:
                mantenimiento_actualizado.fecha_completado = timezone.now()
            
            mantenimiento_actualizado.save()
            mantenimiento_actualizado.save_to_firebase()
            
            # Notificar al solicitante
            Notificacion.objects.create(
                usuario=mantenimiento.solicitante,
                titulo='Actualización de Mantenimiento',
                mensaje=f'El mantenimiento {mantenimiento.numero_ticket} ha sido actualizado',
                tipo='mantenimiento',
                enlace=f'/mantenimientos/{mantenimiento.id}/'
            )
            
            messages.success(request, 'Mantenimiento actualizado exitosamente.')
            return redirect('mantenimientos:detalle', mantenimiento_id=mantenimiento.id)
    else:
        form = GestionarMantenimientoForm(instance=mantenimiento)
    
    return render(request, 'mantenimientos/gestionar.html', {
        'form': form,
        'mantenimiento': mantenimiento
    })


@login_required
def agregar_seguimiento(request, mantenimiento_id):
    """Vista para agregar seguimiento a un mantenimiento"""
    mantenimiento = get_object_or_404(Mantenimiento, id=mantenimiento_id)
    
    # Verificar permisos
    if request.user.tipo_usuario == 'propietario':
        if mantenimiento.inmueble.propietario != request.user:
            messages.error(request, 'No tienes permiso para agregar seguimiento.')
            return redirect('mantenimientos:detalle', mantenimiento_id=mantenimiento.id)
    else:
        if mantenimiento.solicitante != request.user:
            messages.error(request, 'No tienes permiso para agregar seguimiento.')
            return redirect('mantenimientos:detalle', mantenimiento_id=mantenimiento.id)
    
    if request.method == 'POST':
        form = SeguimientoForm(request.POST, request.FILES)
        if form.is_valid():
            seguimiento = form.save(commit=False)
            seguimiento.mantenimiento = mantenimiento
            seguimiento.usuario = request.user
            seguimiento.save()
            
            # Notificar a la otra parte
            if request.user.tipo_usuario == 'propietario':
                destinatario = mantenimiento.solicitante
            else:
                destinatario = mantenimiento.inmueble.propietario
            
            Notificacion.objects.create(
                usuario=destinatario,
                titulo='Nuevo Seguimiento',
                mensaje=f'Nuevo comentario en {mantenimiento.numero_ticket}',
                tipo='mantenimiento',
                enlace=f'/mantenimientos/{mantenimiento.id}/'
            )
            
            messages.success(request, 'Seguimiento agregado exitosamente.')
            return redirect('mantenimientos:detalle', mantenimiento_id=mantenimiento.id)
    else:
        form = SeguimientoForm()
    
    return render(request, 'mantenimientos/agregar_seguimiento.html', {
        'form': form,
        'mantenimiento': mantenimiento
    })


@login_required
def cancelar_mantenimiento(request, mantenimiento_id):
    """Vista para cancelar un mantenimiento"""
    mantenimiento = get_object_or_404(Mantenimiento, id=mantenimiento_id)
    
    # Verificar permisos
    puede_cancelar = False
    if request.user.tipo_usuario == 'propietario' and mantenimiento.inmueble.propietario == request.user:
        puede_cancelar = True
    elif request.user == mantenimiento.solicitante and mantenimiento.estado == 'pendiente':
        puede_cancelar = True
    
    if not puede_cancelar:
        messages.error(request, 'No tienes permiso para cancelar este mantenimiento.')
        return redirect('mantenimientos:detalle', mantenimiento_id=mantenimiento.id)
    
    if request.method == 'POST':
        mantenimiento.estado = 'cancelado'
        mantenimiento.save()
        
        # Notificar
        if request.user.tipo_usuario == 'propietario':
            destinatario = mantenimiento.solicitante
        else:
            destinatario = mantenimiento.inmueble.propietario
        
        Notificacion.objects.create(
            usuario=destinatario,
            titulo='Mantenimiento Cancelado',
            mensaje=f'El mantenimiento {mantenimiento.numero_ticket} ha sido cancelado',
            tipo='mantenimiento',
            enlace=f'/mantenimientos/{mantenimiento.id}/'
        )
        
        messages.success(request, 'Mantenimiento cancelado exitosamente.')
        return redirect('mantenimientos:detalle', mantenimiento_id=mantenimiento.id)
    
    return render(request, 'mantenimientos/confirmar_cancelar.html', {'mantenimiento': mantenimiento})
