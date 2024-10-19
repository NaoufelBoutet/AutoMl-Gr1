from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
#python manage.py test

class LoginViewTests(TestCase):

    def setUp(self):
        # Crée un utilisateur pour les tests d'authentification
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_view_get(self):
        # Teste la requête GET qui doit afficher le formulaire de connexion
        response = self.client.get(reverse('login'))  # Assurez-vous que 'login' est l'URL name pour la vue login_view
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')  # Vérifie que le template utilisé est bien 'login.html'
        self.assertContains(response, '<form')  # Vérifie que la page contient bien un formulaire

    def test_login_view_post_valid(self):
        # Teste la soumission du formulaire avec des identifiants valides
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertRedirects(response, reverse('hello'))  # Vérifie que l'utilisateur est redirigé vers 'hello'
        user = authenticate(username=self.username, password=self.password)
        self.assertIsNotNone(user)  # Vérifie que l'authentification réussit
        self.assertTrue(user.is_authenticated)  # Vérifie que l'utilisateur est bien authentifié

    def test_login_view_post_invalid(self):
        # Teste la soumission du formulaire avec des identifiants invalides
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Le statut doit être 200 (page affichée avec erreur)
        self.assertContains(response, "Invalid username or password.")  # Vérifie que le message d'erreur est bien affiché

    def test_login_view_post_invalid_form(self):
        # Teste la soumission d'un formulaire avec des données vides ou incorrectes
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)  # Le statut doit être 200 (page affichée avec erreur)
        self.assertFormError(response, 'form', 'username', 'This field is required.')  # Vérifie qu'une erreur est affichée pour le champ 'username'
        self.assertFormError(response, 'form', 'password', 'This field is required.')  # Vérifie qu'une erreur est affichée pour le champ 'password'

