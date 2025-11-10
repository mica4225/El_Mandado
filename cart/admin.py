from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)
    
    def subtotal(self, obj):
        return f"${obj.subtotal()}"
    subtotal.short_description = 'Subtotal'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'total_display', 'cantidad_items', 'actualizado_en')
    search_fields = ('usuario__username',)
    readonly_fields = ('creado_en', 'actualizado_en')
    inlines = [CartItemInline]
    
    def total_display(self, obj):
        return f"${obj.total()}"
    total_display.short_description = 'Total'
    
    def cantidad_items(self, obj):
        return obj.cantidad_items()
    cantidad_items.short_description = 'Items'