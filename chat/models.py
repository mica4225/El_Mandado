from django.db import models
from django.conf import settings
from orders.models import Order

class Conversation(models.Model):
    """Conversación entre comprador y vendedor"""
    orden = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='conversaciones') 
    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversaciones_comprador')
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversaciones_vendedor')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-actualizado_en']
        unique_together = ('orden', 'comprador', 'vendedor')
        
    def __str__(self):
        return f"Chat: {self.comprador.username} - {self.vendedor.username} (Orden #{self.orden.pk})"
    
    def ultimo_mensaje(self):
        return self.mensajes.last()


class Message(models.Model):
    """Mensaje individual dentro de una conversación"""
    conversacion = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='mensajes')
    remitente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    leido = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['creado_en']
    
    def __str__(self):
        return f"{self.remitente.username}: {self.texto[:50]}"