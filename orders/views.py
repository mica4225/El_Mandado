import traceback
import io
import mercadopago
import secrets
import hashlib
import base64
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from .models import Order, OrderItem
from .forms import CheckoutForm
from cart.models import Cart
from .services import create_payment_preference, process_mercadopago_payment 
from .utils import obtener_coordenadas_desde_codigo_postal, calcular_costo_envio # Asegúrate de que utils exista
from orders.models import Order

logger = logging.getLogger(__name__)

try:
    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN_FOR_SDK)
    print("Mercado Pago SDK inicializado correctamente.")
except AttributeError:
    # Esto manejaría el caso de que la variable no esté definida en settings
    print("ERROR: MP_ACCESS_TOKEN no encontrado en settings. Se usará token vacío.")
    sdk = mercadopago.SDK("") # SDK inicializado con un token vacío o de prueba

# ============================================
# VISTAS DE COMPRA Y ORDEN
# ============================================

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(usuario=request.user)
    except Cart.DoesNotExist:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('cart_view')
    
    if not cart.items.exists():
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('cart_view')
    
    for item in cart.items.all():
        if item.producto.stock < item.cantidad:
            messages.error(request, f'Stock insuficiente para {item.producto.nombre}')
            return redirect('cart_view')
    
    primer_vendedor = cart.items.first().producto.vendedor
    vendedor_lat, vendedor_lon = obtener_coordenadas_desde_codigo_postal(
        primer_vendedor.codigo_postal if primer_vendedor.codigo_postal else 'C1000'
    )
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        
        if form.is_valid():
            metodo_pago = request.POST.get('metodo_pago')
            
            orden = form.save(commit=False)
            orden.usuario = request.user
            orden.total = cart.total()
            orden.metodo_pago = metodo_pago 
            orden.estado = 'PAGO_PENDIENTE'
            
            # CÁLCULO DE ENVÍO
            if orden.tipo_entrega == 'envio':
                # ⚠️ Necesitas pasar los parámetros necesarios a tu función de cálculo
                orden.costo_envio = 0 # Temporal: calcular_costo_envio(...) 
            else:
                orden.costo_envio = 0

            orden.save()
            
            # Crear items de la orden
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    orden=orden,
                    producto=cart_item.producto,
                    nombre_producto=cart_item.producto.nombre,
                    precio_unitario=cart_item.producto.precio,
                    cantidad=cart_item.cantidad,
                    vendedor=cart_item.producto.vendedor
                )
                # Descontar stock (Se hace aquí al crear la orden)
                #cart_item.producto.stock -= cart_item.cantidad
                #cart_item.producto.save()
            
            # Vaciar carrito
            cart.items.all().delete()
            
            messages.success(request, f'¡Orden #{orden.pk} creada exitosamente!')
            
            # REDIRECCIÓN FINAL
            if orden.metodo_pago == 'EF': 
                return redirect('orders:order_success_cash', order_id=orden.pk) 
            
            elif orden.metodo_pago == 'MP': 
                return redirect('orders:payment_online', order_id=orden.pk)
            
            else:
                messages.success(request, f'¡Orden #{orden.pk} creada. Por favor, realiza el pago!')
                return redirect('orders:order_detail', pk=orden.pk)
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
def order_mark_as_sent(request, order_id):
    """Permite al vendedor marcar una orden PAGADA como ENVIADA."""
    orden = get_object_or_404(Order, pk=order_id)

    # 1. Validar que el usuario es el vendedor de al menos un ítem de la orden
    if not request.user.is_staff and not orden.items.filter(vendedor=request.user).exists():
        messages.error(request, 'No tienes permiso para modificar esta orden.')
        return redirect('orders:seller_orders')

    # 2. Validar estado de transición
    if orden.estado != 'PAGADO':
        messages.warning(request, f'La orden #{orden.pk} debe estar PAGADA para ser enviada.')
        return redirect('orders:order_detail', pk=orden.pk)

    # 3. Marcar como ENVIADO
    orden.estado = 'ENVIADO'
    orden.save(update_fields=['estado'])
    
    messages.success(request, f'La Orden #{orden.pk} ha sido marcada como ENVIADA. Se notificará al cliente.')
    return redirect('orders:order_detail', pk=orden.pk)


@login_required
def order_mark_as_completed(request, order_id):
    """Permite al vendedor marcar una orden ENVIADA o Pagada (Retiro) como COMPLETADA."""
    orden = get_object_or_404(Order, pk=order_id)

    # 1. Validar que el usuario es el vendedor de al menos un ítem de la orden
    if not request.user.is_staff and not orden.items.filter(vendedor=request.user).exists():
        messages.error(request, 'No tienes permiso para modificar esta orden.')
        return redirect('orders:seller_orders')

    # 2. Validar estado de transición (Permitimos Pagado -> Completado para retiros)
    if orden.estado not in ['ENVIADO', 'PAGADO']:
        messages.warning(request, f'La orden #{orden.pk} debe estar ENVIADA o PAGADA para ser completada.')
        return redirect('orders:order_detail', pk=orden.pk)

    # 3. Marcar como COMPLETADO
    orden.estado = 'COMPLETADO'
    orden.save(update_fields=['estado'])

    messages.success(request, f'La Orden #{orden.pk} ha sido marcada como COMPLETADA. ¡Transacción finalizada!')
    return redirect('orders:order_detail', pk=orden.pk)

# ============================================
# VISTA: Página de pago online (Lanza MP o Simulación)
# ============================================
@login_required
def payment_online(request, order_id):
    order = get_object_or_404(Order, pk=order_id, usuario=request.user)

    if order.estado != 'PAGO_PENDIENTE':
        messages.warning(request, "Esta orden ya fue pagada o procesada.")
        return redirect('orders:order_detail', pk=order.pk)

    # 1. Preparar ítems para la preferencia de MP
    items_mp = []
    for item in order.items.all():
        items_mp.append({
            "title": item.nombre_producto,
            "quantity": item.cantidad,
            "unit_price": float(item.precio_unitario),
            "currency_id": "ARS"  # O la moneda que uses
        })
    
    # 2. Definir las URLs de retorno (Webhooks)
    base_url = "https://" + request.get_host() # Obtiene la URL base de tu sitio (Render)
    
    # URLs de Redirección (para cuando el usuario VUELVE del sitio de MP)
    # Success, Pending y Failure son opcionales, pero es buena práctica
    back_urls = {
        "success": f"{base_url}/orders/payment_success_redirect/{order.pk}/",
        "pending": f"{base_url}/orders/payment_pending_redirect/{order.pk}/",
        "failure": f"{base_url}/orders/payment_failure_redirect/{order.pk}/",
    }
    
    # URL de Notificación (Webhook - para cuando MP nos AVISA del pago)
    notification_url = f"{base_url}/orders/mp_webhook/"
    
    # 3. Crear la Preferencia
    preference_data = {
        "items": items_mp,
        "external_reference": str(order.pk), # Usamos el ID de la orden como referencia externa
        "back_urls": back_urls,
        "notification_url": notification_url, 
        "auto_return": "approved",
    }

    try:
        preference = sdk.preference().create(preference_data)
        
        # Guardar el ID de preferencia en la orden (opcional)
        order.mp_preference_id = preference["response"]["id"]
        order.save(update_fields=['mp_preference_id'])
        
        # 4. Redirigir al usuario al link de pago
        return redirect(preference["response"]["init_point"])
    
    except Exception as e:
        messages.error(request, f"Error al crear la preferencia de pago: {e}")
        return redirect('orders:order_detail', pk=order.pk)


# -----------------------------------------------------
# VISTAS DE REDIRECCIÓN (para una mejor UX)
# -----------------------------------------------------

# Estas vistas solo sirven para mostrar un mensaje, el estado real lo define el Webhook.

def payment_success_redirect(request, order_id):
    messages.info(request, "Pago completado. Esperando acreditación de Mercado Pago.")
    return redirect('orders:order_detail', pk=order_id)

def payment_pending_redirect(request, order_id):
    messages.warning(request, "El pago está pendiente de acreditación (ej: en efectivo).")
    return redirect('orders:order_detail', pk=order_id)

def payment_failure_redirect(request, order_id):
    messages.error(request, "El pago fue rechazado. Intenta con otro método.")
    return redirect('orders:order_detail', pk=order_id)

# ============================================
# VISTA MARKETPLACE: Crear la Preferencia de Pago
# ============================================
@login_required
def create_mp_preference(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        order = get_object_or_404(Order, pk=order_id, usuario=request.user)
        result = create_payment_preference(order)
        
        if result.get('init_point'):
            return JsonResponse({"success": True, "init_point": result['init_point']})
        else:
            return JsonResponse({"error": result.get('error', 'Error desconocido.')}, status=400)

    except Exception as e:
        logger.error("💥 ERROR FATAL en create_mp_preference: %s", e)
        return JsonResponse({"error": f"Error interno del servidor."}, status=500)


# ============================================
# VISTA: Simulación de Pago (Opción 2)
# ============================================
@login_required
@transaction.atomic
def simular_pago_exitoso(request, order_id):
    """
    Simula el proceso completo de un pago exitoso, descontando stock.
    """
    order = get_object_or_404(Order, id=order_id, usuario=request.user)

    if order.estado != 'PAGO_PENDIENTE':
        messages.warning(request, f"La orden {order_id} ya ha sido procesada o pagada.")
        return redirect('orders:order_detail', pk=order.id)

    try:
        # 1. Descontar Stock y Validar FINALMENTE
        for item in order.items.all():
            producto = item.producto
            if producto.stock < item.cantidad:
                 # Si el stock no alcanza, se lanza una excepción y se revierte la transacción.
                 raise Exception(f"Stock insuficiente para {producto.nombre} al momento de confirmar el pago.")
            
            producto.stock -= item.cantidad
            producto.save() # Guarda el nuevo stock
        
        # 2. Marcar la Orden como PAGADA
        order.estado = 'PAGADO' 
        order.mp_payment_id = 'SIMULADO-' + str(order.id)
        order.save() 
        
        messages.success(request, f"Pago de la Orden N° {order.id} SIMULADO exitosamente. El pedido está en preparación.")
        
        return redirect('orders:order_detail', pk=order.id)

    except Exception as e:
        # La excepción revierte todos los cambios de stock.
        # Es clave que esta vista esté decorada con @transaction.atomic (como ya lo tienes).
        messages.error(request, f"Falló la validación final del stock/pago: {e}. La orden permanece pendiente.")
        return redirect('orders:order_detail', pk=order.id)
    
@login_required
def simular_pago_fallido(request, pk):
    """
    Simula el escenario en el que un pago es rechazado por la pasarela de pago.
    La orden se mantiene en estado PENDIENTE.
    """
    orden = get_object_or_404(Order, pk=pk, usuario=request.user)
    
    # 1. Puedes opcionalmente cambiar el estado a 'FALLIDO' si lo tienes en tu modelo
    # Pero para la demostración, dejarla en PENDIENTE y mostrar un mensaje es suficiente:
    # orden.estado = 'fallido' # Si tienes este estado
    # orden.save()
    
    # 2. Agregar un mensaje para el usuario
    messages.error(request, f"Pago de la Orden #{orden.pk} rechazado. Intenta nuevamente o elige otro método de pago.")
    
    # 3. Redirigir a la vista de detalle de la orden
    return redirect('orders:order_detail', pk=orden.pk)

# ============================================
# VISTAS DE RETORNO Y IPN (Mercado Pago)
# ============================================
def mp_success_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    # Aquí se debería confiar en el IPN, solo mostrar mensaje
    messages.success(request, f"Pago de la orden #{order.pk} exitoso! Su pedido está siendo procesado.")
    return redirect('orders:order_detail', pk=order.pk)


def mp_failure_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    messages.error(request, f"El pago de la orden #{order.pk} ha fallado. Por favor, intente nuevamente.")
    return redirect('orders:payment_online', order_id=order.pk)


def mp_pending_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    messages.warning(request, f"El pago de la orden #{order.pk} está pendiente de acreditación.")
    return redirect('orders:order_detail', pk=order.pk)

@csrf_exempt
def mp_ipn_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        topic = request.GET.get('topic')
        resource_id = request.GET.get('id')
        
        if topic == 'payment' and resource_id:
            process_mercadopago_payment(resource_id)
            
        return HttpResponse(status=200)

    except Exception as e:
        logger.error("💥 ERROR en IPN: %s", e)
        return HttpResponse(status=200) # Devolver 200 OK para evitar reintentos de MP
    
# ============================================
# VISTAS DE VENDEDOR Y PDF
# ============================================
@login_required
@transaction.atomic
def order_success_cash(request, order_id):
    order = get_object_or_404(Order, pk=order_id, usuario=request.user)
    try:
        if order.estado != 'PAGO_PENDIENTE':
            messages.warning(request, "Esta orden ya fue procesada.")
            return render(request, 'orders/order_success_cash.html', {'order': order})

        # 1. Descontar Stock (Igual que en la simulación)
        for item in order.items.all():
            producto = item.producto
            if producto.stock < item.cantidad:
                raise Exception(f"Stock insuficiente para {producto.nombre} al confirmar efectivo.")
            
            producto.stock -= item.cantidad
            producto.save()
        
        # 2. Marcar como PAGADO (o ENVIADO/COMPLETADO, según tu flujo)
        order.estado = 'PAGADO' # Se asume que el stock se confirma
        order.save()

        messages.success(request, f"Orden #{order.pk} creada. El pago en efectivo será cobrado al retirar/entregar.")
        
    except Exception as e:
        messages.error(request, f"Error al procesar la orden en efectivo: {e}. Por favor, contacte soporte.")

    return render(request, 'orders/order_success_cash.html', {'order': order})


@login_required
def seller_orders(request):
    if not request.user.puede_vender():
        messages.error(request, 'No tenés permisos de vendedor')
        return redirect('home')
    
    order_items = OrderItem.objects.filter(vendedor=request.user).select_related('orden')
    ordenes = {}
    
    for item in order_items:
        ordenes.setdefault(item.orden.pk, {'orden': item.orden, 'items': []})['items'].append(item)
    
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
    
    # Tipo de entrega
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
    
    # Costo de envío y total
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

# ----------------------------------------------------
# VISTAS DE CONEXIÓN MERCADO PAGO (OAuth)
# ----------------------------------------------------

def generate_pkce_codes():
    code_verifier = secrets.token_urlsafe(64)
    hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(hashed).decode('utf-8').replace('=', '')
    return code_verifier, code_challenge


@login_required
def conectar_mercadopago(request):
    if not request.user.puede_vender():
        messages.error(request, "Solo los vendedores pueden conectar su cuenta de Mercado Pago.")
        return redirect('home')
        
    code_verifier, code_challenge = generate_pkce_codes()
    
    request.session['mp_code_verifier'] = code_verifier 
        
    url = (
        f"https://auth.mercadopago.com.ar/authorization?" 
        f"client_id={settings.MP_APP_ID}&"
        f"response_type=code&"
        f"platform_id=mp&" 
        f"redirect_uri={settings.MP_REDIRECT_URI}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )
    return redirect(url)


def callback_mercadopago(request):
    code = request.GET.get('code')
    code_verifier = request.session.pop('mp_code_verifier', None) # Se mantiene para robustez si decides usar PKCE
    
    if not code:
        messages.error(request, "Error de seguridad (PKCE) o código de autorización faltante.")
        return redirect('orders:seller_orders')
        
    try:
        # ⚠️ CORREGIDO: Usar el token principal del Marketplace para inicializar el SDK
        sdk = mercadopago.SDK(settings.MP_MARKETPLACE_ACCESS_TOKEN) 
        
        request_data = {
            "client_secret": settings.MP_CLIENT_SECRET,
            "client_id": settings.MP_APP_ID,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.MP_REDIRECT_URI, 
            #"code_verifier": code_verifier # PKCE
        }
        
        result = sdk.oauth().create_access_token(request_data)

        if 'error' in result:
            logger.error("ERROR API MP: %s - %s", result.get('error'), result.get('message', 'Error desconocido.'))
            messages.error(request, f"Error de la API de Mercado Pago: {result.get('message', 'Error desconocido.')}")
            return redirect('orders:seller_orders')

        token_data = result['response']
        
        # Guardar la info en el objeto CustomUser (Vendedor)
        request.user.mp_access_token = token_data['access_token']
        request.user.mp_refresh_token = token_data.get('refresh_token')
        request.user.mp_user_id = token_data['user_id']
        request.user.save()
        
        messages.success(request, "¡Conexión con Mercado Pago exitosa!")
        
    except Exception as e:
        logger.error("💥 ERROR AL SOLICITAR TOKEN: %s", traceback.format_exc())
        messages.error(request, f"Error interno en la solicitud. {e}")
    
    return redirect('orders:seller_orders')

@csrf_exempt # Importante: MP no envía tokens CSRF
def mp_webhook(request):
    data = request.GET

    if 'data.id' in data and 'type' in data and data['type'] == 'payment':
        payment_id = data['data.id']
        
        # 1. Obtener los detalles del pago desde MP
        try:
            payment_info = sdk.payment().get(payment_id)
            payment_status = payment_info["response"]["status"]
            order_id = payment_info["response"]["external_reference"]

            order = Order.objects.get(pk=order_id)

            # 2. Verificar el estado del pago
            if payment_status == 'approved' and order.estado == 'PAGO_PENDIENTE':
                
                # 3. Marcar como pagado y descontar stock (Lógica Crucial)
                order.estado = 'PAGADO'
                order.mp_payment_id = payment_id # Guardar el ID real de MP
                order.save()
                
                # 4. Descontar Stock (Reutilizamos la lógica del simulador)
                for item in order.items.all():
                    producto = item.producto
                    if producto.stock < item.cantidad:
                         # Debería ser muy raro que esto pase si ya revisamos el stock en checkout
                         # Puedes optar por cancelar la orden o contactar al vendedor
                         # Por ahora, asumimos que el stock es correcto
                         print(f"ALERTA: Stock insuficiente para {producto.nombre} en webhook.")
                         continue 
                    
                    producto.stock -= item.cantidad
                    producto.save(update_fields=['stock'])
                
            elif payment_status in ['pending', 'in_process']:
                 order.estado = 'PAGO_PENDIENTE'
                 order.save(update_fields=['estado'])
                 
            elif payment_status in ['rejected', 'cancelled']:
                 order.estado = 'CANCELADO'
                 order.save(update_fields=['estado'])

            # 5. Siempre debe devolver un 200 OK para que MP sepa que recibimos la notificación
            return HttpResponse(status=200)

        except Order.DoesNotExist:
            return HttpResponse(status=404)
        except Exception as e:
            # Manejo de errores internos
            print(f"Error procesando webhook: {e}")
            return HttpResponse(status=500)
    
    # 6. Responder 200 a cualquier otra cosa para evitar reintentos de MP
    return HttpResponse(status=200)