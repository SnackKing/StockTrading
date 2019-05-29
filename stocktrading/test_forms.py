from django.test import TestCase
from .forms import LoginForm, SignupForm

# Create your tests here.

class TestLoginForm(TestCase):

    def testLoginValid(self):
        valid_data = {
            'email': 'testemail@test.org',
            'password' :'password'
        }
        form = LoginForm(data = valid_data)
        form.is_valid()
        self.assertFalse(form.errors)

    def testLoginInvalidEmail(self):
        valid_data = {
        'email': 'doggo',
        'password': 'password'
        }
        form = LoginForm(data = valid_data)
        form.is_valid()
        self.assertTrue(form.errors)

    def testLoginBlankEmail(self):
        valid_data = {
        'email': '',
        'password': 'password'
        }
        form = LoginForm(data = valid_data)
        form.is_valid()
        self.assertTrue(form.errors)

    def testLoginBlankPassword(self):
        valid_data = {
        'email': 'testemail@test.org',
        'password': ''
        }
        form = LoginForm(data = valid_data)
        form.is_valid()
        self.assertTrue(form.errors)


