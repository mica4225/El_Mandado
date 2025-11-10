from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Category(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True, help_text='Clase de icono Bootstrap')
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.nombre

class Product(models.Model):
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='productos')
    categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='productos')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    imagen_principal = models.ImageField(upload_to='products/')
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    imagen_principal = models.ImageField(
        upload_to='products/',
        blank=False,  # ✅ NO puede estar vacío en forms
        null=False    # ✅ NO puede ser NULL en BD
    )
    
    class Meta:
        ordering = ['-creado_en']
    
    def __str__(self):
        return self.nombre
    
    def disponible(self):
        return self.activo and self.stock > 0
    
    def promedio_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum([r.rating for r in reviews]) / len(reviews)
        return 0

class ProductImage(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='products/gallery/')
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
    
    def __str__(self):
        return f"Imagen de {self.producto.nombre}"