from django.urls import path
from . import views

urlpatterns = [
    path('comparar/', views.price_comparator, name='price_comparator'),
]