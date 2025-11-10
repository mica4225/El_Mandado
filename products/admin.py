from django.contrib import admin
from .models import Category, Product, ProductImage

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'icono')
    search_fields = ('nombre',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 8

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'vendedor', 'categoria', 'precio', 'stock', 'activo', 'creado_en')
    list_filter = ('activo', 'categoria', 'creado_en')
    search_fields = ('nombre', 'descripcion', 'vendedor__username')
    list_editable = ('activo', 'precio', 'stock')
    date_hierarchy = 'creado_en'
    inlines = [ProductImageInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # ✅ Si es superusuario, ve TODO
        if request.user.is_superuser:
            return qs
        # ✅ Si es vendedor, solo ve SUS productos
        return qs.filter(vendedor=request.user)
    
    def has_add_permission(self, request):
        # ✅ Solo vendedores y superusuarios pueden agregar
        return request.user.puede_vender() or request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        # ✅ Solo el dueño o superusuario puede editar
        if request.user.is_superuser:
            return True
        if obj and obj.vendedor == request.user:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        # ✅ Solo el dueño o superusuario puede eliminar
        if request.user.is_superuser:
            return True
        if obj and obj.vendedor == request.user:
            return True
        return False