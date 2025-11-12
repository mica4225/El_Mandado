from .models import Conversation
from .views import get_unread_conversations_count

def user_conversations(request):
    if request.user.is_authenticated:
        return {
            'tiene_conversaciones': Conversation.objects.filter(
                comprador=request.user
            ).exists() or Conversation.objects.filter(
                vendedor=request.user
            ).exists()
        }
    return {}

def unread_messages(request):
    """Añade el contador de conversaciones no leídas al contexto global."""
    return {
        'unread_conversations_count': get_unread_conversations_count(request.user)
    }