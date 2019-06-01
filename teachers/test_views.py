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

class LandingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.session = self.client.session
        self.session.save()

    def test_landing_loggedin(self):
        url = reverse('teachers-landing')
        self.session['tid'] = 'PzHumqmQqzXDhri03TrDe0nEisB3'
        self.session['name'] = 'TestTeacher'
        self.session.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_landing_notloggedin(self):
        url = reverse('teachers-landing')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['tid'] = 'PzHumqmQqzXDhri03TrDe0nEisB3'
        session['name'] = 'TestTeacher'
        session.save()

    def testLoginValid(self):
        url = reverse('teachers-login')
        data = {'email': 'test@teacher.com', 'password': 'password'}
        # Create an instance of a POST request.
        self.response = self.client.post(url, data)
        self.assertRedirects(self.response, reverse('teachers-dashboard'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

    def testLoginInvalid(self):
        url = reverse('teachers-login')
        data = {'email': 'notarealemail@gmail.com', 'password': 'password'}
        # Create an instance of a POST request.
        self.response = self.client.post(url, data)
        self.assertRedirects(self.response, reverse('teachers-login'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

class DashboardTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.client = Client()
        session = self.client.session
        session['tid'] = 'PzHumqmQqzXDhri03TrDe0nEisB3'
        session['name'] = 'TestTeacher'
        session.save()
        self.teacher = db.child('teachers').child(session['tid']).get().val()
        url = reverse('teachers-dashboard')
        self.response = self.client.get(url)

    def test_dashboard_statusCode(self):
        self.assertEqual(self.response.status_code, 200)

    def test_dashboard_data(self):
        self.assertEqual(self.response.context['user'], self.teacher)
    def test_dashboard_name(self):
        self.assertEqual(self.response.context['name'], 'TestTeacher')




