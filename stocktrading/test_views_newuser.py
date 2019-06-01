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
firebase = pyrebase.initialize_app(config)
db = firebase.database()

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

class AddStockTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'TAHqMTTsPEQTpxlZfR8ApRdKxXu1'
        session['name'] = 'BlankUser'
        session.save()

    def test_add(self):
        url = reverse('add-remove-stock')
        data = {'value':'Watch', 'symbol':'TSLA'}
        self.response = self.client.post(url,data)
        added = db.child('users').child('TAHqMTTsPEQTpxlZfR8ApRdKxXu1').child('added').get().val()
        self.assertTrue('TSLA' in added)

    def test_remove(self):
        url = reverse('add-remove-stock')
        data = {'value':'Stop Watching', 'symbol':'MSFT'}
        self.response = self.client.post(url,data)
        added = db.child('users').child('TAHqMTTsPEQTpxlZfR8ApRdKxXu1').child('added').get().val()
        self.assertFalse('MSFT' in added)

    @classmethod
    def tearDownClass(self):
        db.child('users').child('TAHqMTTsPEQTpxlZfR8ApRdKxXu1').child('added').remove()

class TransactionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'TAHqMTTsPEQTpxlZfR8ApRdKxXu1'
        session['name'] = 'BlankUser'
        session.save()
        url = reverse('stocktrading-transactions')
        self.response = self.client.get(url)
 
    def test_getbuys(self):
        self.assertFalse('buys' in self.response.context['transactions'])

    def test_getsells(self):
        self.assertFalse('sells' in self.response.context['transactions'])

class BuyStockTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'TAHqMTTsPEQTpxlZfR8ApRdKxXu1'
        session['name'] = 'TestUser'
        session.save()
        self.user = db.child('users').child('TAHqMTTsPEQTpxlZfR8ApRdKxXu1').get().val()

    
    def test_buyNotOwned(self):
        prevBalance = int(self.user['balance'])
        data = {'price':5,'count':1}
        url = reverse('stocktrading-stock-buy', kwargs={'symbol':"VKTX"})
        self.response = self.client.post(url,data)
        updatedUser = db.child('users').child('TAHqMTTsPEQTpxlZfR8ApRdKxXu1').get().val()
        newBalance = int(updatedUser['balance'])
        self.assertEqual(prevBalance - (int(data['count']) * float(data['price'])), newBalance)

    def test_buyOwned(self):
        prevBalance = int(self.user['balance'])
        data = {'price':10,'count':2}
        url = reverse('stocktrading-stock-buy', kwargs={'symbol':"MSFT"})
        self.response = self.client.post(url,data)
        updatedUser = db.child('users').child('TAHqMTTsPEQTpxlZfR8ApRdKxXu1').get().val()
        newBalance = int(updatedUser['balance'])
        self.assertEqual(prevBalance - (int(data['count']) * float(data['price'])), newBalance)


    def tearDown(self):
        db.child('users').child('TAHqMTTsPEQTpxlZfR8ApRdKxXu1').set(self.user)



