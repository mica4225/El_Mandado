from django.contrib.auth import get_user_model
from products.models import Product, Category
from django.core.files import File
from pathlib import Path

def cargar_datos_demo():
    User = get_user_model()

    # Buscar o crear un vendedor de ejemplo
    vendedor, _ = User.objects.get_or_create(
        username='demo_vendedor',
        defaults={'email': 'vendedor@demo.com', 'password': '123456'}
    )

    # Categorías base
    categorias = [
        "Frutas y Verduras",
        "Lácteos",
        "Panadería",
        "Carnes",
        "Bebidas",
        "Limpieza",
        "Higiene Personal"
    ]

    for nombre in categorias:
        Category.objects.get_or_create(nombre=nombre)

    print("✅ Categorías creadas o existentes")

    # Productos de ejemplo
    productos = [
        {"nombre": "Manzanas rojas", "descripcion": "Manzanas frescas y dulces", "precio": 450.00, "categoria": "Frutas y Verduras"},
        {"nombre": "Leche entera", "descripcion": "1L de leche entera", "precio": 300.00, "categoria": "Lácteos"},
        {"nombre": "Pan casero", "descripcion": "Pan artesanal recien horneado", "precio": 800.00, "categoria": "Panadería"},
        {"nombre": "Carne molida", "descripcion": "Carne vacuna de primera calidad", "precio": 2500.00, "categoria": "Carnes"},
        {"nombre": "Jugo de naranja", "descripcion": "Bebida natural sin azúcar agregada", "precio": 600.00, "categoria": "Bebidas"},
    ]

    imagen_path = Path('media/defaults/demo.jpg')
    if not imagen_path.exists():
        print("⚠️ Imagen demo no encontrada, los productos se crearán sin imagen.")
        imagen_path = None

    for p in productos:
        categoria = Category.objects.filter(nombre=p["categoria"]).first()
        if not categoria:
            continue

        producto, creado = Product.objects.get_or_create(
            nombre=p["nombre"],
            defaults={
                "descripcion": p["descripcion"],
                "precio": p["precio"],
                "categoria": categoria,
                "vendedor": vendedor,
                "stock": 10,
                "activo": True,
            },
        )

        if creado:
            if imagen_path:
                with open(imagen_path, "rb") as f:
                    producto.imagen_principal.save(imagen_path.name, File(f), save=True)
            print(f"✅ Producto creado: {producto.nombre}")
        else:
            print(f"ℹ️ Producto ya existía: {producto.nombre}")

    print("🎉 Base de datos poblada correctamente.")


# Ejecutar automáticamente cuando se carga el módulo
def populate():
    cargar_datos_demo()


if __name__ == "__main__":
    populate()