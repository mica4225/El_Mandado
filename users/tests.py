from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser

# Create your tests here.

class UserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            rol='cliente'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.rol, 'cliente')
        self.assertTrue(self.user.puede_comprar())
        self.assertFalse(self.user.puede_vender())
    
    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser (Cliente)')
    
    def test_switch_to_seller(self):
        self.user.rol = 'vendedor'
        self.user.save()
        self.assertTrue(self.user.puede_vender())

class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
    
    def test_register_view_post(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'rol': 'cliente'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(response.status_code, 302)  # Redirect after success
    
    def test_login_view(self):
        user = CustomUser.objects.create_user(
            username='loginuser',
            password='pass123'
        )
        response = self.client.post(reverse('login'), {
            'username': 'loginuser',
            'password': 'pass123'
        })
        self.assertEqual(response.status_code, 302)