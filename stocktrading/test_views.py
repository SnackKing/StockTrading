from django.test.client import RequestFactory
from django.test import TestCase
from django.test import Client
from . import views
from django.urls import reverse



class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()


    def test_details(self):
        url = reverse('stocktrading-home')
        session = self.client.session
        session['uid'] = '7oGB8hqhrwWbCX3Ie1MLdTb2bGv1'
        session['name'] = 'Zach'
        session.save()
        # Create an instance of a GET request.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)