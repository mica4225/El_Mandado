from django.shortcuts import render
from products.models import Product, Category

# Create your views here.

def home(request):
    productos_destacados = Product.objects.filter(activo=True, stock__gt=0)[:8]
    categorias = Category.objects.all()[:6]
    
    return render(request, 'core/home.html', {
        'productos': productos_destacados,
        'categorias': categorias
    })

def about(request):
    return render(request, 'core/about.html')