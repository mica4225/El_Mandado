from django.db import models
from django.conf import settings
from products.models import Product

# Create your models here.

class Cart(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    def total(self):
        return sum([item.subtotal() for item in self.items.all()])
    
    def cantidad_items(self):
        return sum([item.cantidad for item in self.items.all()])

class CartItem(models.Model):
    carrito = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ('carrito', 'producto')
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
    
    def subtotal(self):
        return self.producto.precio * self.cantidad