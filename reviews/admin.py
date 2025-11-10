from django.contrib import admin
from .models import Review

# Register your models here.

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('producto', 'usuario', 'rating', 'creado_en')
    list_filter = ('rating', 'creado_en')
    search_fields = ('producto__nombre', 'usuario__username', 'comentario')
    readonly_fields = ('creado_en',)
    date_hierarchy = 'creado_en'
    
    # ✅ Solo superusuario puede gestionar reviews
    def has_add_permission(self, request):
        return False  # Las reviews se crean desde el frontend
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser