# populate_on_startup.py
from django.core.management import call_command
from django.db.utils import OperationalError
from django.conf import settings

def populate_if_empty():
    from products.models import Product
    if Product.objects.count() == 0:
        print("🌱 Base vacía. Ejecutando populate_db.py...")
        try:
            call_command('shell', '<', 'populate_db.py')
        except OperationalError:
            print("⚠️ No se pudo conectar a la base de datos todavía.")
    else:
        print("✅ Base ya poblada.")
