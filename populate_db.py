from products.models import Category, Product
from users.models import CustomUser
from django.core.files import File
from pathlib import Path

print("📦 Creando categorías...")

categorias_data = [
    {'nombre': 'Alimentos', 'icono': 'bi-basket'},
    {'nombre': 'Electronica', 'icono': 'bi-laptop'},
    {'nombre': 'Ropa', 'icono': 'bi-bag'},
    {'nombre': 'Hogar', 'icono': 'bi-house'},
    {'nombre': 'Deportes', 'icono': 'bi-trophy'},
    {'nombre': 'Libros', 'icono': 'bi-book'},
]

for cat_data in categorias_data:
    Category.objects.get_or_create(**cat_data)

print("✅ Categorías creadas correctamente.\n")

# Buscar un vendedor existente
vendedor = CustomUser.objects.filter(rol='vendedor').first()
if not vendedor:
    print("No se encontró ningún vendedor. Creá uno antes de ejecutar este script.")
else:
    print("Usando vendedor: {vendedor.username}\n")

    productos_data = [
        {'nombre': 'Arroz Integral 1kg', 'categoria': 'Alimentos', 'precio': 850, 'stock': 50},
        {'nombre': 'Aceite de Oliva 500ml', 'categoria': 'Alimentos', 'precio': 1200, 'stock': 30},
        {'nombre': 'Miel Organica 500g', 'categoria': 'Alimentos', 'precio': 1500, 'stock': 25},
        {'nombre': 'Auriculares Bluetooth', 'categoria': 'Electronica', 'precio': 3500, 'stock': 15},
        {'nombre': 'Mouse Inalambrico', 'categoria': 'Electronica', 'precio': 2000, 'stock': 20},
        {'nombre': 'Remera Algodon', 'categoria': 'Ropa', 'precio': 4000, 'stock': 40},
        {'nombre': 'Buzo Con Capucha', 'categoria': 'Ropa', 'precio': 8500, 'stock': 12},
        {'nombre': 'Almohadones Decorativos', 'categoria': 'Hogar', 'precio': 1800, 'stock': 18},
        {'nombre': 'Set de Toallas', 'categoria': 'Hogar', 'precio': 3200, 'stock': 22},
        {'nombre': 'Colchoneta Yoga', 'categoria': 'Deportes', 'precio': 5000, 'stock': 10},
    ]

    categorias = {cat.nombre: cat for cat in Category.objects.all()}

    print("Creando productos...")

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
                    'descripcion': f'Descripción de {prod_data["nombre"]}. Producto de excelente calidad.',
                    'activo': True
                }
            )

            if created:
                # Si querés agregar una imagen genérica, descomentá esto:
                imagen_path = Path('media/defaults/demo.jpg')
                if imagen_path.exists():
                    with open(imagen_path, 'rb') as f:
                        producto.imagen_principal.save(imagen_path.name, File(f), save=True)
                        print(f"✅ Producto creado: {producto.nombre}")

print("\nBase de datos poblada correctamente.")