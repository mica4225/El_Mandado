from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('switch-to-seller/', views.switch_to_seller, name='switch_to_seller'),
    path('delete-account/', views.delete_account, name='delete_account'),
]