from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.order_list, name='order_list'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    
    # URL de pago online (redirige a MP o Simulación)
    path('pago/online/<int:order_id>/', views.payment_online, name='payment_online'),
    
    # Pago en efectivo
    path('pago/efectivo/<int:order_id>/', views.order_success_cash, name='order_success_cash'),
    
    # 🚨 URL de Simulación de Pago (Opción 2) 🚨
    path('pago/simulacion/<int:order_id>/success/', views.simular_pago_exitoso, name='simular_pago_exitoso'),
    path('pago/simulacion/<int:pk>/failure/', views.simular_pago_fallido, name='simular_pago_fallido'),

    path('seller-orders/', views.seller_orders, name='seller_orders'),
    path('<int:pk>/download/', views.download_order_summary, name='download_order_summary'),

    # URLs para el Vendedor:
    path('mark_sent/<int:order_id>/', views.order_mark_as_sent, name='order_mark_as_sent'),
    path('mark_completed/<int:order_id>/', views.order_mark_as_completed, name='order_mark_as_completed'),

    # Mercado Pago API
    path("mp/create-preference/<int:order_id>/", views.create_mp_preference, name="create_mp_preference"),

    # URLS de retorno de Mercado Pago
    path("mp/success/<int:order_id>/", views.mp_success_view, name="mp_success"),
    path("mp/failure/<int:order_id>/", views.mp_failure_view, name="mp_failure"),
    path("mp/pending/<int:order_id>/", views.mp_pending_view, name="mp_pending"),

    # Vistas de Redirección de MP (UX)
    path('payment_success_redirect/<int:order_id>/', views.payment_success_redirect, name='payment_success_redirect'),
    path('payment_pending_redirect/<int:order_id>/', views.payment_pending_redirect, name='payment_pending_redirect'),
    path('payment_failure_redirect/<int:order_id>/', views.payment_failure_redirect, name='payment_failure_redirect'),

    # 🎯 VISTA CRÍTICA DEL WEBHOOK (backend)
    path('mp_webhook/', views.mp_webhook, name='mp_webhook'),

    # URLS de Conexión OAuth
    path("mp/connect/", views.conectar_mercadopago, name="mp_connect"),
    path("mp-callback/", views.callback_mercadopago, name="mp_callback"), 
    path("mp-ipn-webhook/", views.mp_ipn_webhook, name="mp_ipn_webhook"),
]