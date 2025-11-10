from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:order_id>/', views.payment_process, name='payment_process'),
    path('success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('failure/<int:order_id>/', views.payment_failure, name='payment_failure'),
]