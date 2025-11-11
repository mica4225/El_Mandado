

import os
from pathlib import Path
from django.core.files import File
from django.contrib.auth import get_user_model
from products.models import Category, Product

User = get_user_model()

print("Creando categorías y productos de prueba...")

# ====== Crear categorías ======
categorias_data = [
    {'nombre': 'Alimentos', 'icono': 'bi-basket'},
    {'nombre': 'Electrónica', 'icono': 'bi-laptop'},
    {'nombre': 'Ropa', 'icono': 'bi-bag'},
    {'nombre': 'Hogar', 'icono': 'bi-house'},
    {'nombre': 'Deportes', 'icono': 'bi-trophy'},
    {'nombre': 'Libros', 'icono': 'bi-book'},
]

for cat_data in categorias_data:
    Category.objects.get_or_create(**cat_data)

print("✅ Categorías creadas correctamente.")


# ====== Obtener un vendedor existente ======
vendedor = User.objects.filter(rol='vendedor').first()
if not vendedor:
    print("⚠️ No se encontró ningún usuario con rol 'vendedor'. Creando uno de prueba...")
    vendedor = User.objects.create_user(
        username='vendedor_test',
        password='vendedor123',
        email='vendedor@test.com',
        rol='vendedor'
    )

# ====== Crear productos ======
productos_data = [
    {'nombre': 'Arroz Integral 1kg', 'categoria': 'Alimentos', 'precio': 850, 'stock': 50},
    {'nombre': 'Aceite de Oliva 500ml', 'categoria': 'Alimentos', 'precio': 1200, 'stock': 30},
    {'nombre': 'Miel Orgánica 500g', 'categoria': 'Alimentos', 'precio': 1500, 'stock': 25},
    {'nombre': 'Auriculares Bluetooth', 'categoria': 'Electrónica', 'precio': 3500, 'stock': 15},
    {'nombre': 'Mouse Inalámbrico', 'categoria': 'Electrónica', 'precio': 2000, 'stock': 20},
    {'nombre': 'Remera Algodón', 'categoria': 'Ropa', 'precio': 4000, 'stock': 40},
    {'nombre': 'Buzo Con Capucha', 'categoria': 'Ropa', 'precio': 8500, 'stock': 12},
    {'nombre': 'Almohadones Decorativos', 'categoria': 'Hogar', 'precio': 1800, 'stock': 18},
    {'nombre': 'Set de Toallas', 'categoria': 'Hogar', 'precio': 3200, 'stock': 22},
    {'nombre': 'Colchoneta Yoga', 'categoria': 'Deportes', 'precio': 5000, 'stock': 10},
]

categorias = {cat.nombre: cat for cat in Category.objects.all()}

# Imagen genérica por defecto (asegurate de tenerla en media/defaults/demo.jpg)
imagen_path = Path('media/defaults/demo.jpg')
has_demo_image = imagen_path.exists()

for prod_data in productos_data:
    cat_nombre = prod_data.pop('categoria')
    categoria = categorias.get(cat_nombre)

    if not categoria:
        print(f"⚠️ No se encontró la categoría {cat_nombre}")
        continue

    producto, created = Product.objects.get_or_create(
        nombre=prod_data['nombre'],
        defaults={
            'vendedor': vendedor,
            'categoria': categoria,
            'precio': prod_data['precio'],
            'stock': prod_data['stock'],
            'descripcion': f'{prod_data["nombre"]} - Producto de excelente calidad.',
            'activo': True,
        }
    )

    if created:
        # Si existe una imagen genérica, se la asignamos
        if has_demo_image:
            with open(imagen_path, 'rb') as f:
                producto.imagen_principal.save(imagen_path.name, File(f), save=True)
        print(f"✅ Producto creado: {producto.nombre}")
    else:
        print(f"ℹ️ Producto ya existente: {producto.nombre}")

print("\n🎉 Base de datos poblada correctamente.")
