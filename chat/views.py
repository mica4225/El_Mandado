# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Conversation, Message
from orders.models import Order
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model
from datetime import datetime 
from django.http import HttpResponse

@login_required
def conversation_list(request):
    user = request.user
    # Nota: Tu modelo debe tener campos 'comprador' y 'vendedor' o usar 'participantes' como tu otra vista.
    # Asumo que esta lógica de filtrado es correcta para tu modelo Conversation.
    conversaciones = Conversation.objects.filter(
        Q(comprador=request.user) | Q(vendedor=request.user)
    ).select_related('orden')

    return render(request, 'chat/conversation_list.html', {
        'conversaciones': conversaciones
    })


@login_required
def conversation_detail(request, pk):
    """Vista de una conversación específica que solo maneja GET (renderizado)"""
    conversacion = get_object_or_404(Conversation, pk=pk)
    
    # Verificar que el usuario es parte de la conversación
    if request.user != conversacion.comprador and request.user != conversacion.vendedor:
        return redirect('chat:conversation_list')
    
    # Marcar mensajes como leídos
    conversacion.mensajes.filter(leido=False).exclude(remitente=request.user).update(leido=True)

    mensajes = conversacion.mensajes.all()
    
    # Determinar quién es el otro usuario
    otro_usuario = conversacion.vendedor if request.user == conversacion.comprador else conversacion.comprador
    
    # Obtener el ID del último mensaje para la actualización AJAX
    ultimo_id = mensajes.last().id if mensajes.exists() else 0

    if not mensajes.exists():
        return HttpResponse(f"ERROR: La conversación {pk} no tiene mensajes para el usuario {request.user.username}.")
    
    return render(request, 'chat/conversation_detail.html', {
        'conversacion': conversacion,
        'mensajes': mensajes,
        'otro_usuario': otro_usuario,
        'ultimo_id': ultimo_id,
    })


@login_required
def start_conversation(request, order_id, vendedor_id):
    # Definimos la clase del modelo de usuario
    User = get_user_model() 
    
    order = get_object_or_404(Order, pk=order_id)
    
    # Usamos la clase User
    vendedor = get_object_or_404(User, pk=vendedor_id) 
    
    comprador = order.usuario 
    user = request.user
    
    # 1. Determinar quién es quién
    if user == comprador:
        user1 = comprador
        user2 = vendedor
    elif user == vendedor:
        user1 = vendedor
        user2 = comprador
    else:
        # El usuario logueado no es ni comprador ni vendedor.
        return redirect('home') 
    
    # 2. Buscar si ya existe una conversación (Usando comprador/vendedor si tu modelo los tiene)
    # Nota: Tu modelo debe tener los campos 'comprador' y 'vendedor' o usar 'participantes'
    # Si Conversation tiene campos directos:
    # conversacion = Conversation.objects.filter(order=order, comprador=comprador, vendedor=vendedor).first()
    
    # Si Conversation usa ManyToManyField 'participantes':
    conversacion = Conversation.objects.filter(
        order=order,
        participantes=user1
    ).filter(
        participantes=user2
    ).first()
    
    # 3. Si no existe, crearla
    if not conversacion:
        # Asegúrate de crear la conversación con los campos correctos (order, comprador, vendedor)
        # o añadir participantes si usas ManyToManyField.
        # Asumo que usas ManyToManyField 'participantes' basado en tu código.
        conversacion = Conversation.objects.create(order=order)
        conversacion.participantes.add(user1, user2)
        
    # 4. Redirigir a la vista de detalle de la conversación
    return redirect('chat:conversation_detail', pk=conversacion.pk)
    
# Vistas API (Mantienen el código que evita el 401/HTML)

def get_new_messages(request, conversation_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Sesión expirada o no autorizado.'}, status=401)
        
    try:
        conversacion = get_object_or_404(Conversation, pk=conversation_id)
        last_message_id = request.GET.get('last_id', 0)
        
        try:
            last_message_id = int(last_message_id)
        except ValueError:
            last_message_id = 0
            
        nuevos_mensajes = conversacion.mensajes.filter(id__gt=last_message_id).values(
            'id', 'remitente__username', 'texto', 'creado_en', 'remitente_id' 
        )
        
        return JsonResponse({
            'mensajes': list(nuevos_mensajes), 
            'user_id': request.user.pk 
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def send_message(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Sesión expirada o no autorizado.'}, status=401)
        
    if request.method == "POST":
        texto = request.POST.get("mensaje", "").strip()
        
        if not texto:
            return JsonResponse({'success': False, 'error': 'El mensaje no puede estar vacío.'}, status=400)
            
        conversacion = get_object_or_404(Conversation, pk=pk)
        
        mensaje = Message.objects.create(
            conversacion=conversacion,
            remitente=request.user,
            texto=texto
        )
        
        return JsonResponse({
            'success': True,
            'id': mensaje.pk,
            'remitente_id': request.user.pk, 
            'remitente__username': request.user.username,
            'texto': mensaje.texto,
            'creado_en': mensaje.creado_en.isoformat() 
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

def get_unread_conversations_count(user):
    """Cuenta el número de conversaciones con mensajes no leídos para un usuario."""
    if not user.is_authenticated:
        return 0
    
    # 1. Filtra las conversaciones donde el usuario es el comprador o el vendedor.
    # 2. Cuenta cuántas de esas conversaciones tienen mensajes no leídos
    #    donde el REMITENTE no es el usuario actual.
    
    # Suponiendo que has definido el campo 'leido' en tu modelo Message:
    unread_count = Conversation.objects.filter(
        Q(comprador=user) | Q(vendedor=user)
    ).filter(
        # Filtra las conversaciones que tienen AL MENOS un mensaje no leído,
        # enviado por el otro usuario.
        mensajes__leido=False
    ).exclude(
        # Asegura que esos mensajes no leídos NO fueron enviados por el usuario actual.
        mensajes__remitente=user
    ).distinct().count() # Usamos distinct() para contar solo la conversación, no los mensajes.
    
    return unread_count