from django import template
from chat.models import Conversation # Asegúrate de que 'chat' sea el nombre de tu app

register = template.Library()

@register.filter
def get_conversation_for_user(conversaciones, vendedor_actual):
    """
    Busca la conversación específica entre el comprador (usuario de la orden) 
    y el vendedor_actual.
    """
    try:
        # Esto busca en el queryset (orden.conversaciones.all)
        return conversaciones.get(vendedor=vendedor_actual)
    except Conversation.DoesNotExist:
        return None
    except Exception:
        # Manejo de múltiples resultados si la unicidad falla (debería ser innecesario)
        return conversaciones.filter(vendedor=vendedor_actual).first()