from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from products.models import Product
from orders.models import OrderItem

# Create your views here.

@login_required
def create_review(request, product_id):
    producto = get_object_or_404(Product, pk=product_id)
    
    # Verificar que el usuario compró el producto
    ha_comprado = OrderItem.objects.filter(
        orden__usuario=request.user,
        producto=producto
    ).exists()
    
    if not ha_comprado:
        messages.error(request, 'Solo podés calificar productos que hayas comprado')
        return redirect('product_detail', pk=product_id)
    
    # Verificar que no haya review previo
    if Review.objects.filter(usuario=request.user, producto=producto).exists():
        messages.warning(request, 'Ya dejaste una reseña para este producto')
        return redirect('product_detail', pk=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.usuario = request.user
            review.producto = producto
            
            # Buscar la orden asociada
            orden = OrderItem.objects.filter(
                orden__usuario=request.user,
                producto=producto
            ).first().orden
            review.orden = orden
            
            review.save()
            messages.success(request, '¡Gracias por tu reseña!')
            return redirect('product_detail', pk=product_id)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/create_review.html', {
        'form': form,
        'producto': producto
    })

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, usuario=request.user)
    product_id = review.producto.pk
    review.delete()
    messages.success(request, 'Reseña eliminada')
    return redirect('product_detail', pk=product_id)