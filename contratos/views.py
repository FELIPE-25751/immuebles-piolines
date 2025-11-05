from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Contrato, FirmaDigital
from .forms import ContratoForm, FirmaContratoForm, BusquedaContratoForm
from notificaciones.models import Notificacion
from pagos.models import Pago
from datetime import timedelta
from dateutil.relativedelta import relativedelta


@login_required
def listar_contratos(request):
    """Vista para listar contratos según el tipo de usuario"""
    user = request.user
    form = BusquedaContratoForm(request.GET)
    
    if user.tipo_usuario == 'propietario':
        contratos = Contrato.objects.filter(inmueble__propietario=user)
    else:  # inquilino
        contratos = Contrato.objects.filter(inquilino=user)
    
    # Aplicar filtros
    if form.is_valid():
        estado = form.cleaned_data.get('estado')
        fecha_desde = form.cleaned_data.get('fecha_desde')
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        
        if estado:
            contratos = contratos.filter(estado=estado)
        if fecha_desde:
            contratos = contratos.filter(fecha_inicio__gte=fecha_desde)
        if fecha_hasta:
            contratos = contratos.filter(fecha_fin__lte=fecha_hasta)
    
    paginator = Paginator(contratos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'contratos': page_obj,
        'form': form,
    }
    return render(request, 'contratos/listar.html', context)


@login_required
def detalle_contrato(request, contrato_id):
    """Vista para ver detalles de un contrato"""
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    # Verificar permisos
    if request.user.tipo_usuario == 'propietario':
        if contrato.inmueble.propietario != request.user:
            messages.error(request, 'No tienes permiso para ver este contrato.')
            return redirect('contratos:listar')
    else:
        if contrato.inquilino != request.user:
            messages.error(request, 'No tienes permiso para ver este contrato.')
            return redirect('contratos:listar')
    
    # Obtener pagos relacionados
    pagos = Pago.objects.filter(contrato=contrato).order_by('-fecha_vencimiento')
    
    context = {
        'contrato': contrato,
        'pagos': pagos,
        'requiere_firma': contrato.requiere_firma(request.user),
    }
    return render(request, 'contratos/detalle.html', context)


@login_required
def crear_contrato(request):
    """Vista para crear un nuevo contrato (solo propietarios)"""
    if request.user.tipo_usuario != 'propietario':
        messages.error(request, 'Solo los propietarios pueden crear contratos.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = ContratoForm(request.POST, propietario=request.user)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.estado = 'borrador'
            contrato.save()
            
            # Crear notificación para el inquilino
            Notificacion.objects.create(
                usuario=contrato.inquilino,
                titulo='Nuevo Contrato',
                mensaje=f'Se ha creado un nuevo contrato para {contrato.inmueble.titulo}',
                tipo='contrato',
                enlace=reverse('contratos:detalle', args=[contrato.id])
            )
            
            messages.success(request, 'Contrato creado exitosamente.')
            return redirect('contratos:firmar', contrato_id=contrato.id)
    else:
        form = ContratoForm(propietario=request.user)
    
    return render(request, 'contratos/form.html', {
        'form': form,
        'titulo': 'Crear Contrato'
    })


@login_required
def editar_contrato(request, contrato_id):
    """Vista para editar un contrato (solo en estado borrador)"""
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    # Solo el propietario puede editar
    if contrato.inmueble.propietario != request.user:
        messages.error(request, 'No tienes permiso para editar este contrato.')
        return redirect('contratos:detalle', contrato_id=contrato.id)
    
    # Solo se puede editar si está en borrador
    if contrato.estado != 'borrador':
        messages.error(request, 'Solo se pueden editar contratos en estado borrador.')
        return redirect('contratos:detalle', contrato_id=contrato.id)
    
    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato, propietario=request.user)
        if form.is_valid():
            contrato = form.save(commit=False)
            if contrato.estado == 'borrador':
                contrato.estado = 'pendiente_firma'
            contrato.save()
            messages.success(request, 'Contrato actualizado y listo para firma.')
            return redirect('contratos:detalle', contrato_id=contrato.id)
    else:
        form = ContratoForm(instance=contrato, propietario=request.user)
    
    return render(request, 'contratos/form.html', {
        'form': form,
        'titulo': 'Editar Contrato',
        'contrato': contrato
    })


@login_required
def firmar_contrato(request, contrato_id):
    """Vista para firmar digitalmente un contrato"""
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    # Verificar permisos
    es_propietario = request.user == contrato.inmueble.propietario
    es_inquilino = request.user == contrato.inquilino
    
    if not (es_propietario or es_inquilino):
        messages.error(request, 'No tienes permiso para firmar este contrato.')
        return redirect('contratos:detalle', contrato_id=contrato.id)
    
    # Verificar si ya firmó
    if es_propietario and contrato.firma_propietario:
        messages.info(request, 'Ya has firmado este contrato.')
        return redirect('contratos:detalle', contrato_id=contrato.id)
    
    if es_inquilino and contrato.firma_inquilino:
        messages.info(request, 'Ya has firmado este contrato.')
        return redirect('contratos:detalle', contrato_id=contrato.id)
    
    if request.method == 'POST':
        form = FirmaContratoForm(request.POST)
        if form.is_valid():
            firma = form.cleaned_data['firma']
            
            # Guardar firma
            ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            FirmaDigital.objects.create(
                usuario=request.user,
                firma_base64=firma,
                ip_address=ip,
                user_agent=user_agent
            )
            
            # Actualizar contrato
            if es_propietario:
                contrato.firma_propietario = firma
                contrato.fecha_firma_propietario = timezone.now()
            else:
                contrato.firma_inquilino = firma
                contrato.fecha_firma_inquilino = timezone.now()
            
            # Si ambos firmaron, activar contrato
            if contrato.firma_propietario and contrato.firma_inquilino:
                contrato.estado = 'activo'
                
                # Generar pagos automáticos
                generar_pagos_contrato(contrato)
                
                # Notificar a ambas partes
                Notificacion.objects.create(
                    usuario=contrato.inmueble.propietario,
                    titulo='Contrato Activado',
                    mensaje=f'El contrato {contrato.numero_contrato} ha sido firmado y activado',
                    tipo='contrato',
                    enlace=reverse('contratos:detalle', args=[contrato.id])
                )
                
                Notificacion.objects.create(
                    usuario=contrato.inquilino,
                    titulo='Contrato Activado',
                    mensaje=f'El contrato {contrato.numero_contrato} ha sido firmado y activado',
                    tipo='contrato',
                    enlace=reverse('contratos:detalle', args=[contrato.id])
                )
            else:
                contrato.estado = 'pendiente_firma'
            
            contrato.save()
            contrato.save_to_firebase()
            
            messages.success(request, 'Contrato firmado exitosamente.')
            return redirect('contratos:detalle', contrato_id=contrato.id)
    else:
        form = FirmaContratoForm()
    
    context = {
        'contrato': contrato,
        'form': form,
        'es_propietario': es_propietario,
    }
    return render(request, 'contratos/firmar.html', context)


@login_required
def cancelar_contrato(request, contrato_id):
    """Vista para cancelar un contrato"""
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    # Solo el propietario puede cancelar
    if contrato.inmueble.propietario != request.user:
        messages.error(request, 'No tienes permiso para cancelar este contrato.')
        return redirect('contratos:detalle', contrato_id=contrato.id)
    
    if request.method == 'POST':
        contrato.estado = 'cancelado'
        contrato.save()
        
        # Notificar al inquilino
        Notificacion.objects.create(
            usuario=contrato.inquilino,
            titulo='Contrato Cancelado',
            mensaje=f'El contrato {contrato.numero_contrato} ha sido cancelado',
            tipo='contrato',
            enlace=reverse('contratos:detalle', args=[contrato.id])
        )
        
        messages.success(request, 'Contrato cancelado exitosamente.')
        return redirect('contratos:detalle', contrato_id=contrato.id)
    
    return render(request, 'contratos/confirmar_cancelar.html', {'contrato': contrato})


def generar_pagos_contrato(contrato):
    """Genera los pagos mensuales automáticamente para un contrato"""
    fecha_actual = contrato.fecha_inicio
    numero_pago = 1
    
    while fecha_actual <= contrato.fecha_fin:
        # Calcular fecha de vencimiento
        if fecha_actual.day < contrato.dia_pago:
            fecha_vencimiento = fecha_actual.replace(day=contrato.dia_pago)
        else:
            # Si ya pasó el día de pago este mes, programar para el siguiente
            siguiente_mes = fecha_actual + relativedelta(months=1)
            fecha_vencimiento = siguiente_mes.replace(day=contrato.dia_pago)
        
        # Crear pago
        Pago.objects.create(
            contrato=contrato,
            periodo_inicio=fecha_actual,
            periodo_fin=fecha_actual + relativedelta(months=1) - timedelta(days=1),
            fecha_vencimiento=fecha_vencimiento,
            monto=contrato.get_valor_total_mensual(),
            concepto=f'Arriendo mes {numero_pago}',
            estado='pendiente'
        )
        
        fecha_actual = fecha_actual + relativedelta(months=1)
        numero_pago += 1


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
