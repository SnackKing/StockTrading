from django.test.client import RequestFactory
from django.test import TestCase
from django.test import Client
from . import views
from django.urls import reverse
import pyrebase


config = {
    "apiKey": "AIzaSyAzXh-si71dEDldZkLmbY7l-_NZ8VJTfs4",
    "authDomain": "stocktrader-239615.firebaseapp.com",
    "databaseURL":  "https://stocktrader-239615.firebaseio.com",
    "storageBucket": "stocktrader-239615.appspot.com",
    "serviceAccount": "creds.json"
}

class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'TAHqMTTsPEQTpxlZfR8ApRdKxXu1'
        session['name'] = 'BlankUser'
        session.save()
    

    def test_home(self):
        url = reverse('stocktrading-home')
        # Create an instance of a GET request.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_home_name(self):
        url = reverse('stocktrading-home')
        # Create an instance of a GET request.
        response = self.client.get(url)
        self.assertEqual(response.context['name'], 'BlankUser')

    def test_home_watched_empty(self):
        url = reverse('stocktrading-home')
        # Create an instance of a GET request.
        response = self.client.get(url)
        self.assertEqual(len(response.context['watched']), 0)

    def test_home_owned_empty(self):
        url = reverse('stocktrading-home')
        # Create an instance of a GET request.
        response = self.client.get(url)
        self.assertEqual(len(response.context['owned']), 0)


