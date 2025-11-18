from django.db import models
from django.conf import settings
from products.models import Product

METODO_PAGO_CHOICES = (
    ('MP', 'Mercado Pago (Online)'), 
    ('EF', 'Efectivo al Retirar'),
)

class Order(models.Model):
    STATUS_CHOICES = (
        ('PAGO_PENDIENTE', 'Pago Pendiente'),
        ('PAGADO', 'Pago Recibido'),
        ('ENVIADO', 'Enviado'),
        ('COMPLETADO', 'Completado y Entregado'),
        ('CANCELADO', 'Cancelado'), 
    )

    DELIVERY_CHOICES = (
        ('retiro', 'Retiro en domicilio del vendedor'),
        ('envio', 'Envío a domicilio'),
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ordenes')
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PAGO_PENDIENTE')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    tipo_entrega = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='retiro', verbose_name='Tipo de entrega')
    metodo_pago = models.CharField(max_length=2, choices=METODO_PAGO_CHOICES, default='MP', verbose_name='Método de Pago')
    
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Costo de envío')
    direccion_envio = models.TextField()
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    telefono = models.CharField(max_length=20)
    notas = models.TextField(blank=True)

    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    
    payment_link = models.URLField(max_length=500, blank=True, null=True)
    mp_preference_id = models.CharField(max_length=100, blank=True, null=True)
    mp_payment_id = models.CharField(max_length=100, blank=True, null=True) # Para IPN
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"Orden #{self.pk} - {self.usuario.username}"
        
    def total_con_envio(self):
        return self.total + self.costo_envio

    def save(self, *args, **kwargs):
    # 1. Bandera para verificar si el estado está a punto de cambiar a PAGADO
        is_about_to_be_paid = self.estado == 'PAGADO' and self.pk is not None
    
        try:
            super().save(*args, **kwargs) # 2. Llama al save original para guardar los cambios básicos
        
        # 3. Lógica de Negocio (solo si acaba de ser pagado)
            if is_about_to_be_paid:
            # Aquí iría la lógica de descuento de stock. 
            # Si esta lógica no existe, la puedes dejar vacía por ahora.
            # for item in self.items.all():
            #     item.producto.stock -= item.cantidad
            #     item.producto.save()
                pass 
            
        except Exception as e:
        # 4. 🛑 Si la lógica de negocio (descuento de stock, validación, etc.) falla 🛑
        # Revertir el estado a CANCELADO o PAGO_PENDIENTE y guardar la orden de nuevo.
        # Esto es lo que sospechamos que está ocurriendo en otro lugar.
        
        # Guardar como cancelado para registrar el fallo antes de relanzar el error
            self.estado = 'CANCELADO'
            super().save(update_fields=['estado'])
        
        # Relanza la excepción para que el view (simular_pago_exitoso) la atrape
            raise e

    def mark_as_paid(self):
        """Marca la orden como pagada y ejecuta la lógica necesaria."""
        if self.estado != 'PAGADO':
            self.estado = 'PAGADO'
            # En un entorno real, aquí iría la lógica de notificaciones
            return True
        return False
        
    def update_stock(self):
        """Descuenta el stock de los productos."""
        for item in self.items.all():
            Product = item.producto
            # El stock ya fue descontado en el checkout, esta función debería
            # ser llamada solo si no se descontó antes o para re-chequeo.
            # En la simulación actual, se llamó en el checkout.
            pass


class OrderItem(models.Model):
    orden = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    nombre_producto = models.CharField(max_length=200)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ventas')
    
    def subtotal(self):
        return self.precio_unitario * self.cantidad
    
    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto}"