import mercadopago
from django.conf import settings
from django.shortcuts import reverse 
from django.db import transaction
from django.utils import timezone
from .models import Order 
import os 
import logging

logger = logging.getLogger(__name__)

# ===============================================
# 1. FUNCIÓN PARA CREAR LA PREFERENCIA (MARKETPLACE)
# ===============================================

def create_payment_preference(order):
    vendedor_user = order.items.first().vendedor 
    
    if not vendedor_user or not vendedor_user.mp_access_token:
        logger.error("Error: Vendedor o Access Token no encontrado para la orden %s", order.id)
        return {"error": "El vendedor no ha conectado su cuenta de Mercado Pago."}
        
    # Inicializar SDK con el Access Token del VENDEDOR (correcto para crear preferencia)
    sdk = mercadopago.SDK(vendedor_user.mp_access_token) 
    
    TASA_COMISION = 0.05 
    marketplace_fee = float(order.total) * TASA_COMISION
    
    mp_items = []
    for item in order.items.all():
        mp_items.append({
            "title": item.nombre_producto[:256], 
            "quantity": int(item.cantidad),
            "unit_price": float(item.precio_unitario),
            "currency_id": "ARS",
        })
    
    # Construir BASE_URL dinámicamente usando el host de la redirección
    try:
        host = settings.MP_REDIRECT_URI.split('/orders/')[0]
    except Exception:
        host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', settings.NGROK_HOST)
        host = f"https://{host}"
    
    BASE_URL = host

    preference_data = {
        "items": mp_items,
        "external_reference": str(order.id), 
        "back_urls": {
            "success": f"{BASE_URL}{reverse('orders:mp_success', args=[order.id])}", 
            "failure": f"{BASE_URL}{reverse('orders:mp_failure', args=[order.id])}",
            "pending": f"{BASE_URL}{reverse('orders:mp_pending', args=[order.id])}",
        },
        "notification_url": f"{BASE_URL}{reverse('orders:mp_ipn_webhook')}", # URL para IPN
        "auto_return": "approved",
        "marketplace_fee": round(marketplace_fee, 2), 
    }
    
    preference_response = sdk.preference().create(preference_data)

    if preference_response['status'] in [200, 201]:
        return {"init_point": preference_response['response']['init_point'],
                "preference_id": preference_response['response']['id']}
    
    logger.error("Error al crear preferencia en MP: %s", preference_response.get('response'))
    return {"error": "Error al crear la preferencia de pago en Mercado Pago."}

# ===============================================
# 2. FUNCIÓN PARA PROCESAR EL IPN (WEBHOOK)
# ===============================================

def process_mercadopago_payment(payment_id):
    """Consulta la API de MP para obtener el estado del pago y actualizar la Orden."""
    
    # ⚠️ CORRECCIÓN: Usar el token principal del Marketplace para consultar (o el secreto si es legacy)
    # Asumimos que MP_MARKETPLACE_ACCESS_TOKEN es la mejor opción para consultar pagos.
    sdk = mercadopago.SDK(settings.MP_MARKETPLACE_ACCESS_TOKEN) 
    
    payment_info = sdk.payment().get(payment_id)

    if payment_info['status'] != 200:
        logger.error("Error al consultar el Pago %s: %s", payment_id, payment_info['status'])
        return

    payment = payment_info['response']
    order_id = payment.get('external_reference')
    status = payment.get('status')
    
    if not order_id:
        logger.warning("Pago %s sin external_reference. Ignorado.", payment_id)
        return

    try:
        with transaction.atomic():
            order = Order.objects.get(pk=order_id)
            
            if status == 'approved' and order.estado != 'PAGADO':
                # Al recibir el IPN de pago aprobado, se marca como pagado
                order.mark_as_paid()
                order.mp_payment_id = payment_id
                order.save()
                # ⚠️ Lógica de actualización de stock eliminada aquí, se asume que se manejó en el checkout o en un service aparte si se necesita revertir.
                logger.info("✅ ORDEN %s ACTUALIZADA a PAGADO por IPN.", order_id)
            
            elif status == 'rejected' and order.estado != 'CANCELADO':
                order.estado = 'CANCELADO'
                order.save()
                logger.warning("🚫 ORDEN %s CANCELADA/RECHAZADA por IPN.", order_id)
            
            elif status == 'pending':
                 logger.info("🟡 ORDEN %s PENDIENTE por IPN.", order_id)

    except Order.DoesNotExist:
        logger.error("❓ Orden ID %s no encontrada en la DB.", order_id)
    except Exception as e:
        logger.error("💥 Error al guardar la orden %s: %s", order_id, e)