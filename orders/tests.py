from django.test import TestCase
from users.models import CustomUser
from products.models import Category, Product
from .models import Order, OrderItem

# Create your tests here.

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='buyer',
            password='pass123'
        )
        self.order = Order.objects.create(
            usuario=self.user,
            total=150.00,
            direccion_envio='Calle 123',
            ciudad='Buenos Aires',
            codigo_postal='1000',
            telefono='1234567890'
        )
    
    def test_order_creation(self):
        self.assertEqual(self.order.usuario, self.user)
        self.assertEqual(self.order.estado, 'pendiente')
        self.assertEqual(self.order.total, 150.00)
    
    def test_order_str(self):
        self.assertIn(self.user.username, str(self.order))


