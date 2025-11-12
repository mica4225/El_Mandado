from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem
from .forms import CheckoutForm
from .utils import calcular_costo_envio, obtener_coordenadas_desde_codigo_postal, calcular_distancia
from cart.models import Cart
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import io

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(usuario=request.user)
    except Cart.DoesNotExist:
        messages.error(request, 'Tu carrito está vacío')
        return redirect('cart_view')
    
    if not cart.items.exists():
        messages.error(request, 'Tu carrito está vacío')
        return redirect('cart_view')
    
    # Verificar stock antes del checkout
    for item in cart.items.all():
        if item.producto.stock < item.cantidad:
            messages.error(request, f'Stock insuficiente para {item.producto.nombre}')
            return redirect('cart_view')
    
    # ✅ NUEVO: Obtener coordenadas del vendedor principal (primer producto)
    primer_vendedor = cart.items.first().producto.vendedor
    vendedor_lat, vendedor_lon = obtener_coordenadas_desde_codigo_postal(
        primer_vendedor.codigo_postal if primer_vendedor.codigo_postal else 'C1000'
    )
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                # Crear orden
                orden = form.save(commit=False)
                orden.usuario = request.user
                orden.total = cart.total()
                
                # ✅ CALCULAR COSTO DE ENVÍO
                if orden.tipo_entrega == 'envio':
                    # Obtener coordenadas del comprador
                    comprador_lat, comprador_lon = obtener_coordenadas_desde_codigo_postal(orden.codigo_postal)
                    
                    # Guardar coordenadas
                    orden.latitud = comprador_lat
                    orden.longitud = comprador_lon
                    
                    # Calcular distancia
                    distancia = calcular_distancia(
                        vendedor_lat, vendedor_lon,
                        comprador_lat, comprador_lon
                    )
                    
                    # Calcular costo de envío
                    orden.costo_envio = calcular_costo_envio(distancia)
                    
                    messages.info(
                        request,
                        f'📍 Distancia aproximada: {distancia} km - Costo de envío: ${orden.costo_envio}'
                    )
                else:
                    # Retiro en domicilio del vendedor
                    orden.costo_envio = 0
                    orden.direccion_envio = f"Retiro en: {primer_vendedor.direccion or 'A coordinar'}"
                    orden.ciudad = primer_vendedor.ciudad or 'A coordinar'
                    orden.codigo_postal = primer_vendedor.codigo_postal or ''
                    orden.telefono = primer_vendedor.telefono or ''
                
                orden.save()
                
                # Crear items de la orden y descontar stock
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        orden=orden,
                        producto=cart_item.producto,
                        nombre_producto=cart_item.producto.nombre,
                        precio_unitario=cart_item.producto.precio,
                        cantidad=cart_item.cantidad,
                        vendedor=cart_item.producto.vendedor
                    )
                    
                    # Descontar stock
                    producto = cart_item.producto
                    producto.stock -= cart_item.cantidad
                    producto.save()
                
                # Vaciar carrito
                cart.items.all().delete()
                
                messages.success(request, f'¡Orden #{orden.pk} creada exitosamente!')
                return redirect('payment_process', order_id=orden.pk)
    else:
        form = CheckoutForm(user=request.user)
    
    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart,
        'vendedor_direccion': f"{primer_vendedor.direccion}, {primer_vendedor.ciudad}" if primer_vendedor.direccion else "Dirección no disponible"
    })


@login_required
def order_list(request):
    ordenes = Order.objects.filter(usuario=request.user)
    return render(request, 'orders/order_list.html', {'ordenes': ordenes})


@login_required
def order_detail(request, pk):
    orden = get_object_or_404(Order, pk=pk, usuario=request.user)
    return render(request, 'orders/order_detail.html', {'orden': orden})


@login_required
def seller_orders(request):
    if not request.user.puede_vender():
        messages.error(request, 'No tenés permisos de vendedor')
        return redirect('home')
    
    order_items = OrderItem.objects.filter(vendedor=request.user).select_related('orden')
    ordenes = {}
    
    for item in order_items:
        if item.orden.pk not in ordenes:
            ordenes[item.orden.pk] = {
                'orden': item.orden,
                'items': []
            }
        ordenes[item.orden.pk]['items'].append(item)
    
    return render(request, 'orders/seller_orders.html', {'ordenes': ordenes.values()})


@login_required
def download_order_summary(request, pk):
    orden = get_object_or_404(Order, pk=pk, usuario=request.user)
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Título
    p.setFont("Helvetica-Bold", 20)
    p.drawString(1*inch, height - 1*inch, f"Resumen de Compra #{orden.pk}")
    
    # Info del cliente
    p.setFont("Helvetica", 12)
    y = height - 1.5*inch
    p.drawString(1*inch, y, f"Cliente: {orden.usuario.get_full_name() or orden.usuario.username}")
    y -= 0.3*inch
    p.drawString(1*inch, y, f"Email: {orden.usuario.email}")
    y -= 0.3*inch
    p.drawString(1*inch, y, f"Fecha: {orden.creado_en.strftime('%d/%m/%Y %H:%M')}")
    y -= 0.3*inch
    p.drawString(1*inch, y, f"Estado: {orden.get_estado_display()}")
    
    # ✅ Tipo de entrega
    y -= 0.5*inch
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1*inch, y, f"Tipo de entrega: {orden.get_tipo_entrega_display()}")
    
    # Dirección
    y -= 0.5*inch
    p.setFont("Helvetica-Bold", 14)
    if orden.tipo_entrega == 'envio':
        p.drawString(1*inch, y, "Dirección de Envío:")
    else:
        p.drawString(1*inch, y, "Punto de Retiro:")
    
    p.setFont("Helvetica", 12)
    y -= 0.3*inch
    p.drawString(1*inch, y, orden.direccion_envio)
    y -= 0.3*inch
    p.drawString(1*inch, y, f"{orden.ciudad} - CP: {orden.codigo_postal}")
    y -= 0.3*inch
    p.drawString(1*inch, y, f"Teléfono: {orden.telefono}")
    
    # Productos
    y -= 0.5*inch
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1*inch, y, "Productos:")
    
    p.setFont("Helvetica", 11)
    y -= 0.3*inch
    
    for item in orden.items.all():
        texto = f"{item.cantidad}x {item.nombre_producto} - ${item.precio_unitario} c/u = ${item.subtotal()}"
        p.drawString(1.2*inch, y, texto)
        y -= 0.25*inch
        
        if y < 2*inch:
            p.showPage()
            y = height - 1*inch
            p.setFont("Helvetica", 11)
    
    # ✅ Costo de envío y total
    y -= 0.3*inch
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, y, f"Subtotal: ${orden.total}")
    
    y -= 0.25*inch
    if orden.costo_envio > 0:
        p.drawString(1*inch, y, f"Envío: ${orden.costo_envio}")
    else:
        p.drawString(1*inch, y, "Envío: GRATIS (Retiro en domicilio)")
    
    y -= 0.3*inch
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1*inch, y, f"TOTAL: ${orden.total_con_envio()}")
    
    # Pie de página
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(1*inch, 0.5*inch, "Gracias por tu compra en El Mandado 🌿")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="orden_{orden.pk}.pdf"'
    return response