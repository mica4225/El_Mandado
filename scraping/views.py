from django.shortcuts import render
from .utils import comparar_precios
from products.models import Product

# Create your views here.

def price_comparator(request):
    data = None
    productos_marketplace = []
    
    if request.method == 'GET' and 'q' in request.GET:
        query = request.GET.get('q', '').strip()
        
        if query:
            # Scraping de supermercados
            data = comparar_precios(query)
            
            # Buscar en el marketplace local
            productos_marketplace = Product.objects.filter(
                nombre__icontains=query,
                activo=True,
                stock__gt=0
            )[:5]
    
    return render(request, 'scraping/comparator.html', {
        'data': data,
        'productos_marketplace': productos_marketplace,
        'query': request.GET.get('q', '')
    })