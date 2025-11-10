from django.test import TestCase
from django.urls import reverse
from users.models import CustomUser
from .models import Category, Product

# Create your tests here.

class ProductModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='seller',
            password='pass123',
            rol='vendedor'
        )
        self.category = Category.objects.create(nombre='Test Category')
        self.product = Product.objects.create(
            vendedor=self.user,
            categoria=self.category,
            nombre='Test Product',
            descripcion='Test description',
            precio=100.00,
            stock=10
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.nombre, 'Test Product')
        self.assertEqual(self.product.precio, 100.00)
        self.assertTrue(self.product.disponible())
    
    def test_product_str(self):
        self.assertEqual(str(self.product), 'Test Product')
    
    def test_product_without_stock(self):
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.disponible())

class ProductViewsTest(TestCase):
    def setUp(self):
        self.client.force_login(
            CustomUser.objects.create_user(
                username='seller',
                password='pass123',
                rol='vendedor'
            )
        )
        self.category = Category.objects.create(nombre='Test Category')
    
    def test_product_list_view(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')
    
    def test_product_create_view_get(self):
        response = self.client.get(reverse('product_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_product_create_view_post(self):
        # Este test requiere un archivo de imagen mock
        # Por simplicidad, se omite la creación completa
        pass


