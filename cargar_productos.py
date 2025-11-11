from products.models import Product, Category
from users.models import CustomUser
from django.core.files import File
from pathlib import Path

# Vendedor de prueba
vendedor = User.objects.first()
print(f"Usando vendedor: {vendedor.username}")

# Categorías
categorias = {cat.nombre: cat for cat in Category.objects.all()}

print("Creando productos...")

productos_data = [
    {'nombre': 'Arroz Integral 1kg', 'categoria': 'Alimentos', 'precio': 850, 'stock': 50},
    {'nombre': 'Aceite de Oliva 500ml', 'categoria': 'Alimentos', 'precio': 1200, 'stock': 30},
    {'nombre': 'Miel Orgánica 500g', 'categoria': 'Alimentos', 'precio': 1500, 'stock': 25},
    {'nombre': 'Auriculares Bluetooth', 'categoria': 'Electronica', 'precio': 3500, 'stock': 15},
    {'nombre': 'Mouse Inalámbrico', 'categoria': 'Electronica', 'precio': 2000, 'stock': 20},
    {'nombre': 'Remera Algodón', 'categoria': 'Ropa', 'precio': 4000, 'stock': 40},
    {'nombre': 'Buzo con Capucha', 'categoria': 'Ropa', 'precio': 8500, 'stock': 12},
    {'nombre': 'Almohadones Decorativos', 'categoria': 'Hogar', 'precio': 1800, 'stock': 18},
    {'nombre': 'Set de Toallas', 'categoria': 'Hogar', 'precio': 3200, 'stock': 22},
    {'nombre': 'Colchoneta Yoga', 'categoria': 'Deportes', 'precio': 5000, 'stock': 10},
]

for prod_data in productos_data:
    cat_nombre = prod_data.pop('categoria')
    categoria = categorias.get(cat_nombre)
    if categoria:
        producto, created = Product.objects.get_or_create(
            nombre=prod_data['nombre'],
            defaults={
                'vendedor': vendedor,
                'categoria': categoria,
                'precio': prod_data['precio'],
                'stock': prod_data['stock'],
                'descripcion': f"Descripción de {prod_data['nombre']}. Producto de excelente calidad.",
                'activo': True
            }
        )

        if created:
            imagen_path = Path('media/defaults/demo.jpg')
            if imagen_path.exists():
                producto.imagen.name = 'defaults/demo.jpg'
                producto.save()

print("✅ Productos creados correctamente.")
