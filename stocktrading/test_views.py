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
        session['uid'] = 'rIcUltfYiDNB6lMqdHn2ymdytIN2'
        session['name'] = 'TestUser'
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
        self.assertEqual(response.context['name'], 'TestUser')

    def test_home_owned(self):
        url = reverse('stocktrading-home')
        # Create an instance of a GET request.
        response = self.client.get(url)
        self.assertEqual(len(response.context['owned']), 2)

    def test_home_watched(self):
        url = reverse('stocktrading-home')
        # Create an instance of a GET request.
        response = self.client.get(url)
        self.assertEqual(len(response.context['watched']), 4)

    def test_stock(self):
        url = reverse('stocktrading-stock', kwargs={'symbol':"MSFT"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_stock_watched(self):
        url = reverse('stocktrading-stock', kwargs={'symbol':"MSFT"})
        response = self.client.get(url)
        user = response.context['user']
        self.assertEqual('MSFT' in user['added'], True)

    def test_stock_notwatched(self):
        url = reverse('stocktrading-stock', kwargs={'symbol':"COKE"})
        response = self.client.get(url)
        user = response.context['user']
        self.assertEqual('COKE' in user['added'], False)


