from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal_display',)
    
    def subtotal_display(self, obj):
        return f"${obj.subtotal()}"
    subtotal_display.short_description = 'Subtotal'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'estado', 'total', 'creado_en')
    list_filter = ('estado', 'creado_en')
    search_fields = ('usuario__username', 'usuario__email')
    list_editable = ('estado',)
    date_hierarchy = 'creado_en'
    inlines = [OrderItemInline]
    
    # ✅ Solo superusuarios pueden ver órdenes en el admin
    def has_module_permission(self, request):
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser