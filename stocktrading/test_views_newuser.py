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

class HomeTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'TAHqMTTsPEQTpxlZfR8ApRdKxXu1'
        session['name'] = 'BlankUser'
        session.save()
        url = reverse('stocktrading-home')
        # Create an instance of a GET request.
        self.response = self.client.get(url)
    

    def test_home(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_name(self):
        self.assertEqual(self.response.context['name'], 'BlankUser')

    def test_home_watched_empty(self):
        self.assertEqual(len(self.response.context['watched']), 0)

    def test_home_owned_empty(self):
        self.assertEqual(len(self.response.context['owned']), 0)

class StockTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'TAHqMTTsPEQTpxlZfR8ApRdKxXu1'
        session['name'] = 'BlankUser'
        session.save()
        url = reverse('stocktrading-stock', kwargs={'symbol':"MSFT"})
        self.response = self.client.get(url)
    def test_stock(self):
        self.assertEqual(self.response.status_code, 200)

    def test_stock_watched(self):
        user = self.response.context['user']
        self.assertEqual('added' in user, False)

    def test_stock_newsData(self):
        self.assertEqual(len(self.response.context['newsData']), 5)

    def test_stock_isOwned(self):
        self.assertEqual(self.response.context['owned'], False)

    def test_stock_priceDataExists(self):
        self.assertEqual(len(self.response.context['points']), 4)

    def test_stock_labelsExist(self):
        self.assertEqual(len(self.response.context['dayLabels']), 4)

    def test_stock_numShares(self):
        self.assertEqual(self.response.context['numShares'],0)

    def test_stock_equity(self):
        numShares = self.response.context['numShares']
        price = self.response.context['stock']['price']
        actualEquity = round(int(numShares)*float(price),2)
        self.assertEqual(self.response.context['equity'],actualEquity)


