# populate_db.py - Ejecutar con: python manage.py shell < populate_db.py

from users.models import CustomUser
from products.models import Category, Product
from django.core.files import File
import random

# Crear categorías
categorias_data = [
    {'nombre': 'Alimentos', 'icono': 'bi-basket'},
    {'nombre': 'Electrónica', 'icono': 'bi-laptop'},
    {'nombre': 'Ropa', 'icono': 'bi-bag'},
    {'nombre': 'Hogar', 'icono': 'bi-house'},
    {'nombre': 'Deportes', 'icono': 'bi-trophy'},
    {'nombre': 'Libros', 'icono': 'bi-book'},
]

print("Creando categorías...")
for cat_data in categorias_data:
    Category.objects.get_or_create(**cat_data)

print("✅ Categorías creadas")

# Crear usuarios de prueba
print("\nCreando usuarios de prueba...")

# Cliente
cliente, created = CustomUser.objects.get_or_create(
    username='cliente1',
    defaults={
        'email': 'cliente@test.com',
        'rol': 'cliente',
        'first_name': 'Juan',
        'last_name': 'Pérez'
    }
)
if created:
    cliente.set_password('cliente123')
    cliente.save()
    print(f"✅ Usuario cliente creado: {cliente.username}")

# Vendedor
vendedor, created = CustomUser.objects.get_or_create(
    username='vendedor1',
    defaults={
        'email': 'vendedor@test.com',
        'rol': 'vendedor',
        'first_name': 'María',
        'last_name': 'González'
    }
)
if created:
    vendedor.set_password('vendedor123')
    vendedor.save()
    print(f"✅ Usuario vendedor creado: {vendedor.username}")

# Admin
admin, created = CustomUser.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@test.com',
        'rol': 'admin',
        'first_name': 'Admin',
        'last_name': 'Sistema',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print(f"✅ Usuario admin creado: {admin.username}")

# Crear productos de prueba
print("\nCreando productos de prueba...")

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
            print(f"✅ Producto creado: {producto.nombre}")

print("\n🎉 Base de datos poblada correctamente!")
print("\n📝 Credenciales de prueba:")
print("   Cliente: cliente1 / cliente123")
print("   Vendedor: vendedor1 / vendedor123")
print("   Admin: admin / admin123")