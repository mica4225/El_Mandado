from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
import time

# Create your views here.

@login_required
def payment_process(request, order_id):
    orden = get_object_or_404(Order, pk=order_id, usuario=request.user)
    
    if orden.estado != 'pendiente':
        messages.info(request, 'Esta orden ya fue procesada')
        return redirect('order_detail', pk=order_id)
    
    # Simulación de MercadoPago
    mp_data = {
        'preference_id': f'MP-{orden.pk}-{int(time.time())}',
        'init_point': '#',  # En producción iría la URL real de MP
        'sandbox_init_point': '#'
    }
    
    return render(request, 'payments/process.html', {
        'orden': orden,
        'mp_data': mp_data
    })

@login_required
def payment_success(request, order_id):
    orden = get_object_or_404(Order, pk=order_id, usuario=request.user)
    orden.estado = 'enviado'  # Cambiar a enviado después del pago
    orden.save()
    
    messages.success(request, '¡Pago procesado exitosamente!')
    return render(request, 'payments/success.html', {'orden': orden})

@login_required
def payment_failure(request, order_id):
    orden = get_object_or_404(Order, pk=order_id, usuario=request.user)
    messages.error(request, 'Hubo un problema con el pago. Intentá nuevamente.')
    return render(request, 'payments/failure.html', {'orden': orden})
