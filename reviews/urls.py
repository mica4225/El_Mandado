from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:product_id>/', views.create_review, name='create_review'),
    path('delete/<int:pk>/', views.delete_review, name='delete_review'),
]