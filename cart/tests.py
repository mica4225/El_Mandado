from django.test import TestCase
from users.models import CustomUser
from products.models import Category, Product
from .models import Cart, CartItem

# Create your tests here.

class CartModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='buyer',
            password='pass123'
        )
        self.vendor = CustomUser.objects.create_user(
            username='seller',
            password='pass123',
            rol='vendedor'
        )
        self.category = Category.objects.create(nombre='Test')
        self.product = Product.objects.create(
            vendedor=self.vendor,
            categoria=self.category,
            nombre='Product',
            precio=50.00,
            stock=10
        )
        self.cart = Cart.objects.create(usuario=self.user)
    
    def test_cart_creation(self):
        self.assertEqual(self.cart.usuario, self.user)
        self.assertEqual(self.cart.total(), 0)
    
    def test_add_item_to_cart(self):
        CartItem.objects.create(
            carrito=self.cart,
            producto=self.product,
            cantidad=2
        )
        self.assertEqual(self.cart.total(), 100.00)
        self.assertEqual(self.cart.cantidad_items(), 2)

