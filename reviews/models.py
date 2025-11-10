from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product
from orders.models import Order

# Create your models here.

class Review(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    orden = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)  # Para verificar que compró
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('producto', 'usuario')  # Un review por usuario por producto
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre} ({self.rating}★)"