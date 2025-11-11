# 🌿 El Mandado - Marketplace Local

Marketplace local de productos con comparador de precios, sistema de reviews y carrito persistente.

## 🚀 Características

- ✅ Registro como Cliente o Vendedor
- ✅ CRUD completo de productos con galería de imágenes
- ✅ Carrito de compras persistente
- ✅ Sistema de órdenes y seguimiento
- ✅ Reviews y calificaciones (solo compradores)
- ✅ Comparador de precios con scraping real
- ✅ Pagos simulados (MercadoPago)
- ✅ Generación de PDF de órdenes
- ✅ Panel de administración completo
- ✅ Diseño responsive con tema naturaleza

## 🛠️ Tecnologías

- *Backend:* Django 4.2
- *Frontend:* Bootstrap 5 + CSS Custom
- *Base de datos:* SQLite (desarrollo) / PostgreSQL (producción)
- *Scraping:* BeautifulSoup4 + Requests
- *PDF:* ReportLab

## 📦 Instalación

### 1. Clonar el repositorio
bash
git clone https://github.com/tu-usuario/mercadito.git
cd mercadito


### 2. Crear entorno virtual
bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate


### 3. Instalar dependencias
bash
pip install -r requirements.txt


### 4. Configurar base de datos
bash
python manage.py makemigrations
python manage.py migrate


### 5. Crear superusuario
bash
python manage.py createsuperuser


### 6. Poblar base de datos (opcional)
bash
python manage.py shell < populate_db.py


### 7. Ejecutar servidor
bash
python manage.py runserver


Accedé a: http://127.0.0.1:8000

## 👥 Usuarios de Prueba

Después de ejecutar populate_db.py:

- *Cliente:* cliente1 / cliente123
- *Vendedor:* vendedor1 / vendedor123
- *Admin:* admin / admin123

## 📂 Estructura del Proyecto

mercadito/
├── config/          # Configuración principal
├── users/           # Autenticación y perfiles
├── products/        # Productos y categorías
├── cart/            # Carrito de compras
├── orders/          # Órdenes y checkout
├── reviews/         # Sistema de reseñas
├── scraping/        # Comparador de precios
├── payments/        # Pagos simulados
├── core/            # Vistas generales
├── templates/       # Templates HTML
├── static/          # CSS, JS, imágenes
└── media/           # Archivos subidos


## 🧪 Testing
bash
# Ejecutar todos los tests
python manage.py test

# Tests con coverage
coverage run --source='.' manage.py test
coverage report


## 🚀 Deploy

### PythonAnywhere
Ver sección de deploy más abajo.

### Render
Ver sección de deploy más abajo.

## 📝 Licencia

Este proyecto es educativo y fue creado para fines de aprendizaje.

## 👨‍💻 Autor

Micaela Ailén Ferreira - Proyecto Final Programación