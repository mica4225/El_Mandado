from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.order_list, name='order_list'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('seller-orders/', views.seller_orders, name='seller_orders'),
    path('<int:pk>/download/', views.download_order_summary, name='download_order_summary'),
]