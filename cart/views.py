from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem
from products.models import Product

# Create your views here.

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(usuario=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, pk):
    producto = get_object_or_404(Product, pk=pk, activo=True)
    
    if producto.stock <= 0:
        messages.error(request, 'Producto sin stock')
        return redirect('product_detail', pk=pk)
    
    cart, created = Cart.objects.get_or_create(usuario=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        carrito=cart,
        producto=producto,
        defaults={'cantidad': 1}
    )
    
    if not created:
        if cart_item.cantidad < producto.stock:
            cart_item.cantidad += 1
            cart_item.save()
            messages.success(request, f'{producto.nombre} agregado al carrito')
        else:
            messages.warning(request, f'Stock máximo alcanzado para {producto.nombre}')
    else:
        messages.success(request, f'{producto.nombre} agregado al carrito')
    
    return redirect('product_detail', pk=pk)

@login_required
def update_cart_item(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, carrito__usuario=request.user)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
        if cantidad > 0 and cantidad <= cart_item.producto.stock:
            cart_item.cantidad = cantidad
            cart_item.save()
            messages.success(request, 'Cantidad actualizada')
        else:
            messages.error(request, 'Cantidad inválida')
    
    return redirect('cart_view')

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, carrito__usuario=request.user)
    nombre = cart_item.producto.nombre
    cart_item.delete()
    messages.info(request, f'{nombre} eliminado del carrito')
    return redirect('cart_view')

@login_required
def clear_cart(request):
    cart = get_object_or_404(Cart, usuario=request.user)
    cart.items.all().delete()
    messages.info(request, 'Carrito vaciado')
    return redirect('cart_view')

@login_required
def buy_now(request, pk):
    """Comprar producto directamente con cantidad seleccionable"""
    producto = get_object_or_404(Product, pk=pk, activo=True)
    
    if producto.stock <= 0:
        messages.error(request, 'Producto sin stock')
        return redirect('product_detail', pk=pk)
    
    # Obtener cantidad del POST (si viene)
    cantidad = int(request.POST.get('cantidad', 1)) if request.method == 'POST' else 1
    
    # Validar cantidad
    if cantidad < 1:
        cantidad = 1
    if cantidad > producto.stock:
        cantidad = producto.stock
        messages.warning(request, f'Solo hay {producto.stock} unidades disponibles')
    
    # Obtener o crear carrito
    cart, created = Cart.objects.get_or_create(usuario=request.user)
    
    # Limpiar el carrito
    cart.items.all().delete()
    
    # Agregar el producto con la cantidad seleccionada
    CartItem.objects.create(
        carrito=cart,
        producto=producto,
        cantidad=cantidad
    )
    
    messages.success(request, f'{cantidad}x {producto.nombre} listo para comprar')
    
    # Redirigir directamente al checkout
    return redirect('checkout')