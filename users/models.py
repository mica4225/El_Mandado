from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
        ('admin', 'Administrador'),
    )
    
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cliente')
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    avatar = models.ImageField(upload_to='users/', blank=True, null=True)
    
    # Evitar conflictos con auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    def puede_vender(self):
        return self.rol in ['vendedor', 'admin']
    
    def puede_comprar(self):
        return True  # Todos pueden comprar