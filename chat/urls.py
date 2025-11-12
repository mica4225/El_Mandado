from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('<int:pk>/', views.conversation_detail, name='conversation_detail'), 
    path('<int:pk>/send/', views.send_message, name='send_message'),
    path('iniciar/<int:order_id>/<int:vendedor_id>/', views.start_conversation, name='start_conversation'),
    path('api/mensajes/<int:conversation_id>/', views.get_new_messages, name='get_new_messages'),
]
