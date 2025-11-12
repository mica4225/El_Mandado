from django.db import models
from django.conf import settings
from products.models import Product

# Create your models here.

class Order(models.Model):
    STATUS_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    )
    DELIVERY_CHOICES = (
        ('retiro', 'Retiro en domicilio del vendedor'),
        ('envio', 'Envío a domicilio'),
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ordenes')
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    tipo_entrega = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default='retiro',
        verbose_name='Tipo de entrega'
    )
    
    # ✅ NUEVO: Costo de envío
    costo_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Costo de envío'
    )
    
    # Datos de envío (solo si tipo_entrega = 'envio')
    direccion_envio = models.TextField()
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    telefono = models.CharField(max_length=20)
    notas = models.TextField(blank=True)
    
    # ✅ NUEVO: Coordenadas para calcular distancia
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    
    # Timestamps
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"Orden #{self.pk} - {self.usuario.username}"

class OrderItem(models.Model):
    orden = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    nombre_producto = models.CharField(max_length=200)  # Por si se borra el producto
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ventas')
    
    def subtotal(self):
        return self.precio_unitario * self.cantidad
    
    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto}"