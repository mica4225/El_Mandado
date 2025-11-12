from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, ProductImage
from .forms import ProductForm, ProductImageForm

# Create your views here.

def product_list(request):
    productos = Product.objects.filter(activo=True, stock__gt=0)
    categorias = Category.objects.all()
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('q')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
        'busqueda': busqueda,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    producto = get_object_or_404(Product, pk=pk, activo=True)
    imagenes_adicionales = producto.imagenes.all()[:8]
    reviews = producto.reviews.all()
    
    # ✅ PRODUCTOS RELACIONADOS (misma categoría, excluyendo el actual)
    productos_relacionados = Product.objects.filter(
        categoria=producto.categoria,
        activo=True,
        stock__gt=0
    ).exclude(pk=pk)[:4]  # Máximo 4 productos
    
    context = {
        'producto': producto,
        'imagenes': imagenes_adicionales,
        'reviews': reviews,
        'productos_relacionados': productos_relacionados,  # ✅ NUEVO
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def my_products(request):
    if not request.user.puede_vender():
        messages.error(request, 'Necesitás ser vendedor para acceder a esta sección')
        return redirect('home')
    
    productos = Product.objects.filter(vendedor=request.user)
    return render(request, 'products/my_products.html', {'productos': productos})

@login_required
def product_create(request):
    if not request.user.puede_vender():
        messages.error(request, 'Necesitás ser vendedor para publicar productos')
        return redirect('switch_to_seller')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.vendedor = request.user
            producto.save()
            messages.success(request, 'Producto creado correctamente')
            return redirect('product_add_images', pk=producto.pk)
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {'form': form, 'titulo': 'Crear Producto'})

@login_required
def product_edit(request, pk):
    producto = get_object_or_404(Product, pk=pk, vendedor=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente')
            return redirect('my_products')
    else:
        form = ProductForm(instance=producto)
    
    return render(request, 'products/product_form.html', {'form': form, 'titulo': 'Editar Producto', 'producto': producto})

@login_required
def product_delete(request, pk):
    producto = get_object_or_404(Product, pk=pk, vendedor=request.user)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente')
        return redirect('my_products')
    return render(request, 'products/product_confirm_delete.html', {'producto': producto})

@login_required
def product_add_images(request, pk):
    producto = get_object_or_404(Product, pk=pk, vendedor=request.user)
    
    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            imagen = form.save(commit=False)
            imagen.producto = producto
            
            # Verificar límite de 8 imágenes
            if producto.imagenes.count() >= 8:
                messages.error(request, 'Máximo 8 imágenes adicionales por producto')
            else:
                imagen.save()
                messages.success(request, 'Imagen agregada')
        
        # Si hace clic en "Finalizar"
        if 'finalizar' in request.POST:
            return redirect('my_products')
    
    form = ProductImageForm()
    imagenes = producto.imagenes.all()
    
    return render(request, 'products/product_add_images.html', {
        'form': form,
        'producto': producto,
        'imagenes': imagenes,
    })

@login_required
def product_delete_image(request, pk):
    imagen = get_object_or_404(ProductImage, pk=pk, producto__vendedor=request.user)
    producto_id = imagen.producto.pk
    imagen.delete()
    messages.success(request, 'Imagen eliminada')
    return redirect('product_add_images', pk=producto_id)