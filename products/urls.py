from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('my-products/', views.my_products, name='my_products'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('<int:pk>/add-images/', views.product_add_images, name='product_add_images'),
    path('image/<int:pk>/delete/', views.product_delete_image, name='product_delete_image'),
]