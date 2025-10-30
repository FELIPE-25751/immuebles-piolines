from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import HttpResponse
from .models import Pago, RegistroPago
from .forms import RegistrarPagoForm, FiltrarPagosForm
from notificaciones.models import Notificacion
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import io


@login_required
def listar_pagos(request):
    """Vista para listar pagos según el tipo de usuario"""
    user = request.user
    form = FiltrarPagosForm(request.GET)
    
    if user.tipo_usuario == 'propietario':
        pagos = Pago.objects.filter(contrato__inmueble__propietario=user)
    else:  # inquilino
        pagos = Pago.objects.filter(contrato__inquilino=user)
    
    # Aplicar filtros
    if form.is_valid():
        estado = form.cleaned_data.get('estado')
        fecha_desde = form.cleaned_data.get('fecha_desde')
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        
        if estado:
            pagos = pagos.filter(estado=estado)
        if fecha_desde:
            pagos = pagos.filter(fecha_vencimiento__gte=fecha_desde)
        if fecha_hasta:
            pagos = pagos.filter(fecha_vencimiento__lte=fecha_hasta)
    
    # Actualizar moras para pagos vencidos
    for pago in pagos.filter(estado='vencido'):
        pago.calcular_mora()
    
    paginator = Paginator(pagos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pagos': page_obj,
        'form': form,
    }
    return render(request, 'pagos/listar.html', context)


@login_required
def detalle_pago(request, pago_id):
    """Vista para ver detalles de un pago"""
    pago = get_object_or_404(Pago, id=pago_id)
    
    # Verificar permisos
    if request.user.tipo_usuario == 'propietario':
        if pago.contrato.inmueble.propietario != request.user:
            messages.error(request, 'No tienes permiso para ver este pago.')
            return redirect('pagos:listar')
    else:
        if pago.contrato.inquilino != request.user:
            messages.error(request, 'No tienes permiso para ver este pago.')
            return redirect('pagos:listar')
    
    registros = pago.registros.all()
    
    context = {
        'pago': pago,
        'registros': registros,
    }
    return render(request, 'pagos/detalle.html', context)


@login_required
def registrar_pago(request, pago_id):
    """Vista para registrar un pago"""
    pago = get_object_or_404(Pago, id=pago_id)
    
    # Solo inquilinos pueden registrar pagos de sus contratos
    if pago.contrato.inquilino != request.user and request.user.tipo_usuario != 'propietario':
        messages.error(request, 'No tienes permiso para registrar este pago.')
        return redirect('pagos:detalle', pago_id=pago.id)
    
    if request.method == 'POST':
        form = RegistrarPagoForm(request.POST, request.FILES)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.pago = pago
            registro.registrado_por = request.user
            registro.save()
            
            # Actualizar monto pagado
            pago.monto_pagado += registro.monto
            
            # Si es el primer pago, establecer fecha de pago
            if not pago.fecha_pago:
                pago.fecha_pago = timezone.now().date()
            
            pago.save()
            pago.save_to_firebase()
            
            # Notificar al propietario
            if request.user.tipo_usuario == 'inquilino':
                Notificacion.objects.create(
                    usuario=pago.contrato.inmueble.propietario,
                    titulo='Nuevo Pago Registrado',
                    mensaje=f'Se ha registrado un pago de ${registro.monto:,.0f} para {pago.concepto}',
                    tipo='pago',
                    enlace=f'/pagos/{pago.id}/'
                )
            
            messages.success(request, 'Pago registrado exitosamente.')
            return redirect('pagos:detalle', pago_id=pago.id)
    else:
        # Pre-llenar con el saldo pendiente
        initial_data = {
            'monto': pago.get_saldo_pendiente()
        }
        form = RegistrarPagoForm(initial=initial_data)
    
    context = {
        'form': form,
        'pago': pago,
    }
    return render(request, 'pagos/registrar.html', context)


@login_required
def marcar_pagado(request, pago_id):
    """Permite al propietario marcar un pago como pagado (registro automático)."""
    pago = get_object_or_404(Pago, id=pago_id)

    # Solo el propietario del inmueble puede usar esta acción
    if pago.contrato.inmueble.propietario != request.user:
        messages.error(request, 'No tienes permiso para cambiar el estado de este pago.')
        return redirect('pagos:detalle', pago_id=pago.id)

    if request.method != 'POST':
        return redirect('pagos:detalle', pago_id=pago.id)

    # Si ya está pagado, no hacer nada
    if pago.estado == 'pagado':
        messages.info(request, 'Este pago ya está marcado como pagado.')
        return redirect('pagos:detalle', pago_id=pago.id)

    # Registrar un registro de pago automático con el saldo pendiente
    saldo = pago.get_saldo_pendiente()
    if saldo > 0:
        registro = RegistroPago.objects.create(
            pago=pago,
            monto=saldo,
            metodo_pago='otro',
            referencia='Marcado como pagado por el propietario',
            registrado_por=request.user
        )
        pago.monto_pagado += registro.monto

    # Establecer fecha de pago si no existe
    if not pago.fecha_pago:
        pago.fecha_pago = timezone.now().date()

    pago.save()
    pago.save_to_firebase()

    # Notificar al inquilino
    Notificacion.objects.create(
        usuario=pago.contrato.inquilino,
        titulo='Pago confirmado por el propietario',
        mensaje=f'El propietario ha marcado como pagado el pago {pago.numero_pago}.',
        tipo='pago',
        enlace=f'/pagos/{pago.id}/'
    )

    messages.success(request, 'Pago marcado como pagado correctamente.')
    return redirect('pagos:detalle', pago_id=pago.id)


@login_required
def marcar_vencido(request, pago_id):
    """Permite al propietario marcar un pago como vencido manualmente."""
    pago = get_object_or_404(Pago, id=pago_id)

    # Solo el propietario del inmueble puede usar esta acción
    if pago.contrato.inmueble.propietario != request.user:
        messages.error(request, 'No tienes permiso para cambiar el estado de este pago.')
        return redirect('pagos:detalle', pago_id=pago.id)

    if request.method != 'POST':
        return redirect('pagos:detalle', pago_id=pago.id)

    if pago.estado == 'vencido':
        messages.info(request, 'Este pago ya está marcado como vencido.')
        return redirect('pagos:detalle', pago_id=pago.id)

    pago.estado = 'vencido'
    pago.calcular_mora()
    pago.save()
    pago.save_to_firebase()

    Notificacion.objects.create(
        usuario=pago.contrato.inquilino,
        titulo='Pago marcado como vencido',
        mensaje=f'El propietario ha marcado como vencido el pago {pago.numero_pago}.',
        tipo='pago',
        enlace=f'/pagos/{pago.id}/'
    )

    messages.success(request, 'Pago marcado como vencido.')
    return redirect('pagos:detalle', pago_id=pago.id)


@login_required
def generar_cuenta_cobro(request, pago_id):
    """Genera una cuenta de cobro en PDF"""
    pago = get_object_or_404(Pago, id=pago_id)
    
    # Verificar permisos
    if request.user.tipo_usuario == 'propietario':
        if pago.contrato.inmueble.propietario != request.user:
            messages.error(request, 'No tienes permiso para generar esta cuenta de cobro.')
            return redirect('pagos:listar')
    else:
        if pago.contrato.inquilino != request.user:
            messages.error(request, 'No tienes permiso para ver esta cuenta de cobro.')
            return redirect('pagos:listar')
    
    # Crear el PDF en memoria
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    titulo = Paragraph("<b>CUENTA DE COBRO</b>", styles['Title'])
    elements.append(titulo)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del pago
    info_data = [
        ['Número de Pago:', pago.numero_pago],
        ['Contrato:', pago.contrato.numero_contrato],
        ['Concepto:', pago.concepto],
        ['Período:', f'{pago.periodo_inicio} - {pago.periodo_fin}'],
        ['Fecha Vencimiento:', str(pago.fecha_vencimiento)],
        ['', ''],
        ['Valor Arriendo:', f'${pago.contrato.valor_arriendo:,.2f}'],
        ['Valor Administración:', f'${pago.contrato.valor_administracion:,.2f}'],
        ['Mora:', f'${pago.mora:,.2f}'],
        ['', ''],
        ['<b>TOTAL A PAGAR:</b>', f'<b>${pago.get_monto_total():,.2f}</b>'],
    ]
    
    tabla = Table(info_data, colWidths=[3*inch, 3*inch])
    tabla.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(tabla)
    elements.append(Spacer(1, 0.5*inch))
    
    # Información del propietario e inquilino
    propietario = pago.contrato.inmueble.propietario
    inquilino = pago.contrato.inquilino
    
    partes_info = Paragraph(f"""
        <b>Beneficiario:</b> {propietario.get_full_name()}<br/>
        <b>Cédula:</b> {propietario.cedula}<br/>
        <b>Teléfono:</b> {propietario.telefono}<br/>
        <br/>
        <b>Pagador:</b> {inquilino.get_full_name()}<br/>
        <b>Cédula:</b> {inquilino.cedula}<br/>
        <b>Inmueble:</b> {pago.contrato.inmueble.titulo}<br/>
        <b>Dirección:</b> {pago.contrato.inmueble.direccion}
    """, styles['Normal'])
    
    elements.append(partes_info)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Actualizar registro de generación
    if not pago.cuenta_cobro_generada:
        pago.cuenta_cobro_generada = True
        pago.fecha_generacion_cuenta = timezone.now()
        pago.save()
    
    # Retornar PDF
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cuenta_cobro_{pago.numero_pago}.pdf"'
    
    return response


@login_required
def reportes_pagos(request):
    """Vista para generar reportes de pagos"""
    if request.user.tipo_usuario != 'propietario':
        messages.error(request, 'Solo los propietarios pueden ver reportes.')
        return redirect('pagos:listar')
    
    # Estadísticas generales
    pagos = Pago.objects.filter(contrato__inmueble__propietario=request.user)
    
    total_pagos = pagos.filter(estado='pagado').count()
    total_pendientes = pagos.filter(estado='pendiente').count()
    total_vencidos = pagos.filter(estado='vencido').count()
    
    # Montos
    from django.db.models import Sum
    monto_recibido = pagos.filter(estado='pagado').aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0
    monto_pendiente = pagos.filter(estado__in=['pendiente', 'vencido']).aggregate(Sum('monto'))['monto__sum'] or 0
    monto_mora = pagos.filter(estado='vencido').aggregate(Sum('mora'))['mora__sum'] or 0
    
    context = {
        'total_pagos': total_pagos,
        'total_pendientes': total_pendientes,
        'total_vencidos': total_vencidos,
        'monto_recibido': monto_recibido,
        'monto_pendiente': monto_pendiente,
        'monto_mora': monto_mora,
        'pagos_recientes': pagos.order_by('-fecha_creacion')[:10],
    }
    
    return render(request, 'pagos/reportes.html', context)
