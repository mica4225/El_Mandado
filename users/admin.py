from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'mostrar_rol', 'first_name', 'last_name', 'is_staff')  # ← Cambiar 'rol' por 'mostrar_rol'
    list_filter = ('rol', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def mostrar_rol(self, obj):
        if obj.is_superuser:
            return "🔑 Superusuario"
        return obj.get_rol_display()
    mostrar_rol.short_description = 'Rol'
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'telefono', 'direccion', 'ciudad', 'codigo_postal', 'avatar')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'email', 'telefono')
        }),
    )
    
    def has_module_permission(self, request):
        return request.user.is_staff
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_module_permission(self, request):
        return request.user.is_superuser