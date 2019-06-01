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

class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'rIcUltfYiDNB6lMqdHn2ymdytIN2'
        session['name'] = 'TestUser'
        session.save()

    def testLoginValid(self):
        url = reverse('stocktrading-login')
        data = {'email': 'allegrettidev@gmail.com', 'password': 'password'}
        # Create an instance of a POST request.
        self.response = self.client.post(url, data)
        self.assertRedirects(self.response, reverse('stocktrading-home'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

    def testLoginInvalid(self):
        url = reverse('stocktrading-login')
        data = {'email': 'notarealemail@gmail.com', 'password': 'password'}
        # Create an instance of a POST request.
        self.response = self.client.post(url, data)
        self.assertRedirects(self.response, reverse('stocktrading-login'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

  
class SignOutTest(TestCase):
    def testSignOutValid(self):
        self.client = Client()
        url = reverse('stocktrading-login')
        data = {'email': 'allegrettidev@gmail.com', 'password': 'password'}
        session = self.client.session
        session['uid'] = 'rIcUltfYiDNB6lMqdHn2ymdytIN2'
        session['name'] = 'TestUser'
        session.save()
        self.response = self.client.post(url, data)
        logoutUrl = reverse('stocktrading-signout')
        self.response = self.client.get(logoutUrl)
        self.assertRedirects(self.response, reverse('stocktrading-landing'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        self.assertFalse('name' in self.client.session)
        self.assertFalse('uid' in self.client.session)


    def testSignoutInvalid(self):
        logoutUrl = reverse('stocktrading-signout')
        self.response = self.client.get(logoutUrl)
        self.assertRedirects(self.response, reverse('stocktrading-landing'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        self.assertFalse('name' in self.client.session)
        self.assertFalse('uid' in self.client.session)







class HomeTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'rIcUltfYiDNB6lMqdHn2ymdytIN2'
        session['name'] = 'TestUser'
        session.save()
        url = reverse('stocktrading-home')
        # Create an instance of a GET request.
        self.response = self.client.get(url)
    

    def test_home(self):
        self.assertEqual(self.response.status_code, 200)
    def test_home_name(self):
        self.assertEqual(self.response.context['name'], 'TestUser')

    def test_home_owned(self):
        self.assertEqual(len(self.response.context['owned']), 2)

    def test_home_watched(self):
        self.assertEqual(len(self.response.context['watched']), 4)

class StockTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'rIcUltfYiDNB6lMqdHn2ymdytIN2'
        session['name'] = 'TestUser'
        session.save()
        url = reverse('stocktrading-stock', kwargs={'symbol':"MSFT"})
        self.response = self.client.get(url)
    def test_stock(self):
        self.assertEqual(self.response.status_code, 200)

    def test_stock_watched(self):
        user = self.response.context['user']
        self.assertEqual('MSFT' in user['added'], True)

    def test_stock_notwatched(self):
        user = self.response.context['user']
        self.assertEqual('COKE' in user['added'], False)

    def test_stock_newsData(self):
        self.assertEqual(len(self.response.context['newsData']), 5)

    def test_stock_isOwned(self):
        self.assertEqual(self.response.context['owned'], True)

    def test_stock_priceDataExists(self):
        self.assertEqual(len(self.response.context['points']), 4)

    def test_stock_labelsExist(self):
        self.assertEqual(len(self.response.context['dayLabels']), 4)

    def test_stock_numShares(self):
        self.assertEqual(self.response.context['numShares'],'1')

    def test_stock_equity(self):
        numShares = self.response.context['numShares']
        price = self.response.context['stock']['price']
        actualEquity = round(int(numShares)*float(price),2)
        self.assertEqual(self.response.context['equity'],actualEquity)

class AddStockTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'rIcUltfYiDNB6lMqdHn2ymdytIN2'
        session['name'] = 'TestUser'
        session.save()

    def test_add(self):
        url = reverse('add-remove-stock')
        data = {'value':'Watch', 'symbol':'TSLA'}
        self.response = self.client.post(url,data)
        added = db.child('users').child('rIcUltfYiDNB6lMqdHn2ymdytIN2').child('added').get().val()
        self.assertTrue('TSLA' in added)

    def test_remove(self):
        url = reverse('add-remove-stock')
        data = {'value':'Stop Watching', 'symbol':'MSFT'}
        self.response = self.client.post(url,data)
        added = db.child('users').child('rIcUltfYiDNB6lMqdHn2ymdytIN2').child('added').get().val()
        self.assertFalse('MSFT' in added)

    @classmethod
    def tearDownClass(self):
        db.child('users').child('rIcUltfYiDNB6lMqdHn2ymdytIN2').child('added').child('TSLA').remove()
        db.child("users").child('rIcUltfYiDNB6lMqdHn2ymdytIN2').child("added").update({'MSFT': "doggo"})

class TransactionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'rIcUltfYiDNB6lMqdHn2ymdytIN2'
        session['name'] = 'TestUser'
        session.save()
        url = reverse('stocktrading-transactions')
        self.response = self.client.get(url)
        self.trans = db.child('users').child('rIcUltfYiDNB6lMqdHn2ymdytIN2').child('orders').get().val()
 
    def test_getbuys(self):
        self.assertEqual(self.trans['buy'], self.response.context['transactions']['buys'])

    def test_getsells(self):
        self.assertEqual(self.trans['sell'], self.response.context['transactions']['sells'])

class BuyStockTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['uid'] = 'rIcUltfYiDNB6lMqdHn2ymdytIN2'
        session['name'] = 'TestUser'
        session.save()
        self.user = db.child('users').child('rIcUltfYiDNB6lMqdHn2ymdytIN2').get().val()

    
    def test_buyNotOwned(self):
        prevBalance = int(self.user['balance'])
        data = {'price':5,'count':1}
        url = reverse('stocktrading-stock-buy', kwargs={'symbol':"VKTX"})
        self.response = self.client.post(url,data)
        updatedUser = db.child('users').child('rIcUltfYiDNB6lMqdHn2ymdytIN2').get().val()
        newBalance = int(updatedUser['balance'])
        self.assertEqual(prevBalance - (int(data['count']) * float(data['price'])), newBalance)

    def test_buyOwned(self):
        prevBalance = int(self.user['balance'])
        data = {'price':10,'count':2}
        url = reverse('stocktrading-stock-buy', kwargs={'symbol':"MSFT"})
        self.response = self.client.post(url,data)
        updatedUser = db.child('users').child('rIcUltfYiDNB6lMqdHn2ymdytIN2').get().val()
        newBalance = int(updatedUser['balance'])
        self.assertEqual(prevBalance - (int(data['count']) * float(data['price'])), newBalance)


    def tearDown(self):
        db.child('users').child('rIcUltfYiDNB6lMqdHn2ymdytIN2').set(self.user)





      







