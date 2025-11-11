"""
WSGI config for mercadito project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mercadito.settings')

application = get_wsgi_application()

from django.conf import settings

if os.environ.get('ON_RENDER') == 'true':
    try:
        from django.core.management import call_command
        print("🚀 Ejecutando populate_db.py automáticamente en Render...")
        os.system('python manage.py shell < populate_db.py')
    except Exception as e:
        print(f"❌ Error al ejecutar populate_db.py: {e}")