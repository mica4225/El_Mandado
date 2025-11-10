#!/usr/bin/env bash
set -o errexit

# 1. Instalar dependencias (Render hace esto automáticamente si tienes requirements.txt)
pip install -r requirements.txt 

# 2. Ejecutar migraciones
python manage.py migrate --noinput

# 3. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Nota: Render ejecutará este script. Si no defines el pip install
# en buildCommand, asegúrate de que Render lo haga por defecto.
# Incluirlo aquí asegura que las librerías estén antes de las migraciones/collectstatic.