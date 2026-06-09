from urllib import response
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core import mail
from accounts.forms import CustomUserCreationForm


class RegisterViewTest(TestCase):
    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIn('user_form', response.context)

    def test_register_view_post_valid_envia_email_e_cria_usuario(self):
        form_data = {
            'email': 'usuario@teste.com'
        }
        response = self.client.post(reverse('register'), data=form_data)
        
        #verifica redireção(registro bem-sucedido)
        self.assertEqual(response.status_code, 302)
        #verifica se user foi criado no bd
        self.assertTrue(User.objects.filter(email='usuario@teste.com').exists())
        #verifica se email foi enviado
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Sua senha é:', mail.outbox[0].body)
         
         
    def test_register_view_post_invalid(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'testpassword123',
            'password2': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIn('user_form', response.context)
        self.assertFalse(User.objects.filter(username='newuser').exists())

class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIn('login_form', response.context)

    def test_login_view_post_valid(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redireciona após login bem-sucedido
        self.assertRedirects(response, reverse('evento_list'))

    def test_login_view_post_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIn('login_form', response.context)

class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redireciona após logout
        self.assertRedirects(response, reverse('home'))

class CustomUserCreationFormTest(TestCase):
    def test_form_valido(self):
        form_data = {
            'username': 'testuser',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form_data = {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'differentpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
    # Verifica se os widgets têm a classe 'form-control'
    def test_custom_widgets(self):
        form = CustomUserCreationForm()
        self.assertIn('class="form-control"', form.as_p())  